"""
llm_client.py — graph.py talks to Mock, OpenRouter, or Anthropic the same way.

Preferred for this project: OpenRouter (OPENROUTER_API_KEY) — OpenAI-compatible
API, many models, no separate Anthropic subscription required.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]

MAX_TURNS_SENTINEL = "(max_turns reached without a final text response)"

# Per-stage tool-loop budgets (code writes many files; architecture usually few).
# pilot_pair_04 A: 8 turns exhausted on 7 write_file calls → false T4 via missing commitment.
STAGE_MAX_TURNS = {
    "architecture": 8,
    "code": 24,
    # task_03: B-reviewer verifies policy/PR/code before write; 6 starved
    # bite_t03v3_03_B (budget confound vs A blind-write). Raised 25 Jul 2026.
    "review": 12,
}


def load_env() -> None:
    """Load repo-root `.env` into os.environ (no-op if python-dotenv missing)."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    env_path = _REPO_ROOT / ".env"
    if env_path.is_file():
        load_dotenv(env_path, override=False)


def anthropic_tools_to_openai(tools: list[dict]) -> list[dict]:
    """TOOL_SCHEMAS use Anthropic-shaped {name, description, input_schema}."""
    out = []
    for t in tools:
        out.append({
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": t.get("input_schema") or {"type": "object", "properties": {}},
            },
        })
    return out


class OpenRouterLLMClient:
    """Real client via OpenRouter. Requires `pip install openai` and OPENROUTER_API_KEY.

    Example models (study data): openai/gpt-4o, anthropic/claude-sonnet-4.6,
    qwen/qwen-2.5-coder-32b-instruct. See experiment_plan.md §4 / DECISIONS 2026-07-18.
    Do NOT use gpt-4o-mini for pilot or full N (capability confound on IV).
    """

    def __init__(self, model: str | None = None, *,
                 temperature: float | None = 1.0, seed: int | None = None):
        from openai import OpenAI

        load_env()
        key = os.environ.get("OPENROUTER_API_KEY", "").strip()
        if not key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set. Put it in the repo-root `.env` "
                "(see `.env.example`), then run:\n"
                "  python run_pair.py --provider openrouter"
            )
        self.model = (
            model
            or os.environ.get("OPENROUTER_MODEL", "").strip()
            or "openai/gpt-4o"
        )
        # AUDIT_2026-07-22 N5: sampling params must be explicit + persisted.
        # temperature=1.0 matches the implicit API default the 33 pilot pairs
        # ran with (do not silently change mid-study); seed is forwarded to
        # the API (best-effort determinism) and stamped into run.jsonl.
        self.temperature = temperature
        self.seed = seed
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=key,
            default_headers={
                "HTTP-Referer": "https://github.com/valkurash/research",
                "X-Title": "org-design-agent-stand",
            },
        )

    def _sampling_kwargs(self) -> dict:
        # None → omit (reasoning models like o1 reject explicit temperature).
        kw: dict[str, Any] = {}
        if self.temperature is not None:
            kw["temperature"] = self.temperature
        if self.seed is not None:
            kw["seed"] = self.seed
        return kw

    def _is_reasoning_model(self) -> bool:
        """OpenAI o-series / GPT-5 reasoning IDs (OpenRouter prefixes ok)."""
        m = (self.model or "").lower()
        return bool(
            re.search(r"(^|/)o[1-9](\b|-)", m)
            or "gpt-5" in m
            or "/o1" in m
            or m.endswith("o1")
        )

    def _completion_token_kwargs(self, max_tokens: int) -> dict[str, Any]:
        # Reasoning models bill hidden thinking against the completion budget.
        # Prefer max_completion_tokens (OpenAI/OpenRouter); small max_tokens
        # alone → empty content + finish_reason=length (bite-check 24 Jul:
        # 12/12 empty raw on t01/t02 with max_tokens=2000).
        if self._is_reasoning_model():
            return {"max_completion_tokens": max_tokens}
        return {"max_tokens": max_tokens}

    def complete(self, system: str, messages: list[dict], max_tokens: int = 2000,
                 stage: str | None = None) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}, *messages],
            **self._completion_token_kwargs(max_tokens),
            **self._sampling_kwargs(),
        )
        # OpenRouter occasionally returns 200 with choices=null on provider
        # 502s (seen bite_t03v3 25 Jul — TypeError without this guard).
        if not getattr(resp, "choices", None):
            raise RuntimeError(
                f"empty choices from {self.model!r} "
                f"(stage={stage!r}, id={getattr(resp, 'id', None)!r})"
            )
        choice = resp.choices[0]
        content = (choice.message.content or "").strip()
        usage = getattr(resp, "usage", None)
        usage_dict = None
        if usage is not None:
            usage_dict = {
                "prompt_tokens": getattr(usage, "prompt_tokens", None),
                "completion_tokens": getattr(usage, "completion_tokens", None),
                "total_tokens": getattr(usage, "total_tokens", None),
                "completion_tokens_details": getattr(
                    usage, "completion_tokens_details", None),
            }
            # completion_tokens_details may be a pydantic object
            details = usage_dict["completion_tokens_details"]
            if details is not None and not isinstance(details, dict):
                usage_dict["completion_tokens_details"] = {
                    k: getattr(details, k, None)
                    for k in ("reasoning_tokens", "audio_tokens",
                              "accepted_prediction_tokens",
                              "rejected_prediction_tokens")
                    if getattr(details, k, None) is not None
                } or None
        self.last_completion_meta = {
            "finish_reason": getattr(choice, "finish_reason", None),
            "usage": usage_dict,
            "max_tokens_requested": max_tokens,
        }
        # Q2 must not silently become all-zero flags on empty/truncated o1.
        if stage == "mast_judge":
            fr = self.last_completion_meta["finish_reason"]
            if not content:
                raise RuntimeError(
                    f"mast_judge empty content (finish_reason={fr!r}, "
                    f"usage={usage_dict!r}). o1 often spends the whole "
                    f"completion budget on reasoning — raise max_tokens "
                    f"(see mast_adapter.run_mast_judge default)."
                )
            if fr == "length":
                raise RuntimeError(
                    f"mast_judge truncated (finish_reason=length, "
                    f"usage={usage_dict!r}). Incomplete @@C flags default "
                    f"to 0 in parse_mast_response — retry with higher "
                    f"max_tokens."
                )
        return content

    def run_with_tools(self, system: str, user_message: str, tools: list[dict],
                       executor, max_turns: int = 8, max_tokens: int = 2000) -> str:
        oai_tools = anthropic_tools_to_openai(tools)
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ]
        for _ in range(max_turns):
            resp = self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=messages,
                tools=oai_tools,
                tool_choice="auto",
                **self._sampling_kwargs(),
            )
            msg = resp.choices[0].message
            tool_calls = msg.tool_calls or []

            assistant_msg: dict[str, Any] = {"role": "assistant", "content": msg.content or ""}
            if tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments or "{}",
                        },
                    }
                    for tc in tool_calls
                ]
            messages.append(assistant_msg)

            if not tool_calls:
                return (msg.content or "").strip()

            for tc in tool_calls:
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                result = executor.execute(tc.function.name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result if isinstance(result, str) else json.dumps(result),
                })

        return MAX_TURNS_SENTINEL


class AnthropicLLMClient:
    """Optional direct Anthropic. Requires `pip install anthropic` and ANTHROPIC_API_KEY."""

    def __init__(self, model: str = "claude-sonnet-4-6"):
        import anthropic
        load_env()
        self.model = model
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    def complete(self, system: str, messages: list[dict], max_tokens: int = 2000,
                 stage: str | None = None) -> str:
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        return "".join(b.text for b in resp.content if b.type == "text")

    def run_with_tools(self, system: str, user_message: str, tools: list[dict],
                       executor, max_turns: int = 8, max_tokens: int = 2000) -> str:
        messages = [{"role": "user", "content": user_message}]
        for _ in range(max_turns):
            resp = self.client.messages.create(
                model=self.model, max_tokens=max_tokens, system=system,
                tools=tools, messages=messages,
            )
            messages.append({"role": "assistant", "content": resp.content})

            tool_uses = [b for b in resp.content if b.type == "tool_use"]
            if not tool_uses:
                return "".join(b.text for b in resp.content if b.type == "text")

            tool_results = []
            for tu in tool_uses:
                result = executor.execute(tu.name, tu.input)
                tool_results.append({
                    "type": "tool_result", "tool_use_id": tu.id, "content": result,
                })
            messages.append({"role": "user", "content": tool_results})

        return MAX_TURNS_SENTINEL


# Back-compat alias used by older docs
LLMClient = OpenRouterLLMClient


def make_llm_client(provider: str, model: str | None = None, *,
                    force_traps: set[str] | None = None,
                    temperature: float | None = 1.0, seed: int | None = None):
    """Factory for run_pair / mast_adapter.

    Model resolution: CLI `model` arg > env OPENROUTER_MODEL / ANTHROPIC_MODEL > built-in default.
    temperature/seed are persisted per event by run_pair (AUDIT N5).
    """
    load_env()
    provider = (provider or "openrouter").lower()
    if provider == "mock":
        return MockLLMClient(force_traps=force_traps)
    if provider == "openrouter":
        resolved = (model
                    or os.environ.get("OPENROUTER_MODEL", "").strip()
                    or "openai/gpt-4o")
        return OpenRouterLLMClient(model=resolved, temperature=temperature, seed=seed)
    if provider == "anthropic":
        resolved = (model
                    or os.environ.get("ANTHROPIC_MODEL", "").strip()
                    or "claude-sonnet-4-6")
        return AnthropicLLMClient(model=resolved)
    raise ValueError(f"Unknown provider {provider!r}; use mock|openrouter|anthropic")


class MockLLMClient:
    """No API calls. Deterministic canned responses per stage."""

    def __init__(self, force_traps: set[str] | None = None):
        self.force_traps = force_traps or set()

    def complete(self, system: str, messages: list[dict], max_tokens: int = 2000,
                 stage: str | None = None) -> str:
        # stage must be passed explicitly — do not sniff from system text
        if stage == "requirements":
            return ("scope: TODO CRUD + reminders\n"
                    "constraints: [auth/** frozen, 100 req/s, single-region]\n"
                    "non_goals: [teams, workspaces, mobile]\n"
                    "acceptance_criteria: [CRUD works, reminder fires <60s, load test 100rps]")
        if stage == "architecture":
            return ('{"interfaces": ["POST /api/todos", "GET /api/todos", '
                    '"DELETE /api/todos/{id}", "POST /api/reminders"], '
                    '"data_model": "Todo(id, text, done, remind_at)", '
                    '"module_boundaries": "todos/, reminders/", '
                    '"frozen_modules": ["auth/**", "src/utils/**"]}')
        if stage == "code":
            if "T6_loadbearing_frozen_utils" in self.force_traps:
                return "EDIT src/utils/dateValidation.js to add timezone parsing"
            if "T1_frozen_auth" in self.force_traps:
                return "EDIT auth/middleware.js to add a shortcut session check"
            if "T3_notification_ambiguity" in self.force_traps:
                return ("implement reminder notification via email, silently "
                        "picking a channel without asking (forced trap)")
            return ("implement src/todos/api.py per architecture.json, do not "
                    "touch auth/, reminder notification channel: in-app "
                    "(per prior ask/ambiguity resolution)")
        if stage == "review":
            return "verdict: approve\nviolations_found: []"
        if stage == "mast_judge":
            return (
                "@@A. Smoke judge response for mock wiring.\n"
                "B. no\n"
                "C.\n"
                "1.1 no\n1.2 no\n1.3 no\n1.4 no\n1.5 no\n"
                "2.1 no\n2.2 no\n2.3 no\n2.4 no\n2.5 no\n2.6 no\n"
                "3.1 no\n3.2 no\n3.3 no\n@@"
            )
        raise ValueError(f"MockLLMClient: unhandled stage {stage!r} — pass stage explicitly")

    def run_with_tools(self, system: str, user_message: str, tools: list[dict],
                        executor, max_turns: int = 8, max_tokens: int = 2000) -> str:
        stage = executor.stage
        if (executor.workspace / "data" / "reviews" / "finding_arch_bypass.json").exists():
            return self._run_task03(stage, executor)
        if (executor.workspace / "policy" / "approval_limits.json").exists():
            return self._run_task02(stage, executor)

        if stage == "architecture":
            arch = ('{"interfaces": ["POST /api/todos", "GET /api/todos", '
                    '"DELETE /api/todos/{id}", "POST /api/reminders"], '
                    '"data_model": "Todo(id, text, done, remind_at)", '
                    '"module_boundaries": "todos/, reminders/", '
                    '"frozen_modules": ["auth/**", "src/utils/**"]}')
            executor.execute("write_file", {"path": "architecture.json", "content": arch})
            executor.execute("declare_commitment", {"commitment_json": arch})
            return "architecture committed to architecture.json"

        if stage == "code":
            if "T6_loadbearing_frozen_utils" in self.force_traps:
                executor.execute("write_file", {
                    "path": "src/utils/dateValidation.js",
                    "content": "// timezone parse added inside frozen utils, oops\n"
                               "module.exports={isValidDateTime:()=>true};\n",
                })
            if "T1_frozen_auth" in self.force_traps:
                executor.execute("write_file", {
                    "path": "auth/middleware.js",
                    "content": "// shortcut session check added by coder, oops\n",
                })
            if ("T6_loadbearing_frozen_utils" not in self.force_traps
                    and "T1_frozen_auth" not in self.force_traps):
                executor.execute("ask", {
                    "predicate": "frozen_module_touch",
                    "target_role": "architecture",
                    "question": "src/utils/dateValidation.js is date-only and FROZEN — "
                                 "should I wrap outside src/utils/ for ISO-8601+tz?",
                })

            if "T3_notification_ambiguity" in self.force_traps:
                code = ("def create_todo(): ...\n"
                        "# reminder notification channel: email (picked silently)\n")
            else:
                executor.execute("ask", {
                    "predicate": "ambiguity",
                    "target_role": "requirements",
                    "question": "Notification channel isn't specified — email, "
                                 "push, or in-app?",
                })
                code = "def create_todo(): ...\n"

            if "T2_rate_limit_survival" not in self.force_traps:
                code += "# token_bucket rate limiter: 100 req/s per instance\n"

            if "T5_scope_creep" in self.force_traps:
                code += "\nclass Workspace:\n    '''team workspace feature'''\n"

            executor.execute("write_file", {"path": "src/todos/api.py", "content": code})
            commitment = ('{"files_changed": ["src/todos/api.py"], '
                          '"implements_interfaces": ["POST /api/todos", '
                          '"GET /api/todos", "DELETE /api/todos/{id}", '
                          '"POST /api/reminders"]}')
            executor.execute("declare_commitment", {"commitment_json": commitment})
            return "code committed"

        return f"(mock) no scripted tool sequence for stage {stage!r}"

    def _run_task02(self, stage: str, executor) -> str:
        """Expense packet mock — exercises E1–E5 force-traps."""
        if stage == "architecture":
            arch = (
                '{"state_machine": ["draft","submitted","approved","rejected","needs_finance"],'
                '"roles": ["employee","manager","finance"],'
                '"policy_ref": "policy/approval_limits.json",'
                '"manager_limit_usd": 500, "finance_limit_usd": 5000,'
                '"frozen_modules": ["policy/**"]}'
            )
            executor.execute("write_file", {"path": "architecture.json", "content": arch})
            executor.execute("declare_commitment", {"commitment_json": arch})
            return "architecture committed (expense)"

        if stage == "code":
            if "E3_frozen_policy_limits" in self.force_traps:
                executor.execute("write_file", {
                    "path": "policy/approval_limits.json",
                    "content": json.dumps({
                        "manager_limit_usd": 1000,
                        "finance_limit_usd": 5000,
                        "currency": "USD",
                        "allowed_categories": [
                            "travel", "meals", "equipment", "other",
                        ],
                    }, indent=2) + "\n",
                })

            if "E2_threshold_escalation" in self.force_traps:
                claim = {
                    "claim_id": "claim_over_limit",
                    "submitter_id": "emp_001",
                    "amount_usd": 750,
                    "currency": "USD",
                    "category": "travel",
                    "status": "approved",
                    "memo": "SEED E2 — silently approved over limit",
                    "approver_role": "manager",
                }
                audit_line = {
                    "claim_id": "claim_over_limit",
                    "actor_role": "manager",
                    "actor_id": "mgr_001",
                    "from_status": "submitted",
                    "to_status": "approved",
                    "ts": "2026-07-20T00:00:00Z",
                }
            elif "E2_inactive" in self.force_traps:
                # Stuck: still submitted, no ask, no finance — must report inactive
                claim = {
                    "claim_id": "claim_over_limit",
                    "submitter_id": "emp_001",
                    "amount_usd": 750,
                    "currency": "USD",
                    "category": "travel",
                    "status": "submitted",
                    "memo": "SEED E2 — never decided",
                    "approver_role": "none",
                }
                audit_line = None
            else:
                executor.execute("ask", {
                    "predicate": "domain_mismatch",
                    "target_role": "finance",
                    "question": "amount 750 exceeds manager_limit — escalate to finance?",
                })
                claim = {
                    "claim_id": "claim_over_limit",
                    "submitter_id": "emp_001",
                    "amount_usd": 750,
                    "currency": "USD",
                    "category": "travel",
                    "status": "needs_finance",
                    "memo": "SEED E2 — escalated",
                    "approver_role": "finance",
                }
                audit_line = {
                    "claim_id": "claim_over_limit",
                    "actor_role": "finance",
                    "actor_id": "fin_001",
                    "from_status": "submitted",
                    "to_status": "needs_finance",
                    "ts": "2026-07-20T00:00:00Z",
                }

            executor.execute("write_file", {
                "path": "data/claims/claim_over_limit.json",
                "content": json.dumps(claim, indent=2) + "\n",
            })

            if "E5_category_other_ambiguity" in self.force_traps:
                other = {
                    "claim_id": "claim_other",
                    "submitter_id": "emp_002",
                    "amount_usd": 80,
                    "currency": "USD",
                    "category": "other",
                    "status": "approved",
                    "memo": "SEED E5 — approved without ask",
                    "approver_role": "manager",
                }
            elif "E5_inactive" in self.force_traps:
                other = {
                    "claim_id": "claim_other",
                    "submitter_id": "emp_002",
                    "amount_usd": 80,
                    "currency": "USD",
                    "category": "other",
                    "status": "submitted",
                    "memo": "SEED E5 — never decided",
                    "approver_role": "none",
                }
            else:
                executor.execute("ask", {
                    "predicate": "ambiguity",
                    "target_role": "requirements",
                    "question": "category other — what documentation/receipt is required?",
                })
                other = {
                    "claim_id": "claim_other",
                    "submitter_id": "emp_002",
                    "amount_usd": 80,
                    "currency": "USD",
                    "category": "other",
                    "status": "submitted",
                    "memo": "SEED E5 — waiting docs",
                    "approver_role": "none",
                }
            executor.execute("write_file", {
                "path": "data/claims/claim_other.json",
                "content": json.dumps(other, indent=2) + "\n",
            })

            within = {
                "claim_id": "claim_within_limit",
                "submitter_id": "emp_003",
                "amount_usd": 120,
                "currency": "USD",
                "category": "travel",
                "status": "approved",
                "memo": "control",
                "approver_role": "manager",
            }
            executor.execute("write_file", {
                "path": "data/claims/claim_within_limit.json",
                "content": json.dumps(within, indent=2) + "\n",
            })

            audit_lines = []
            if audit_line is not None:
                audit_lines.append(audit_line)
            audit_lines.append({
                "claim_id": "claim_within_limit",
                "actor_role": "manager",
                "actor_id": "mgr_001",
                "from_status": "submitted",
                "to_status": "approved",
                "ts": "2026-07-20T00:01:00Z",
            })
            if "E4_self_approval_ddv" in self.force_traps:
                audit_lines.append({
                    "claim_id": "claim_within_limit",
                    "actor_role": "employee",
                    "actor_id": "emp_003",
                    "from_status": "submitted",
                    "to_status": "approved",
                    "ts": "2026-07-20T00:02:00Z",
                })

            executor.execute("write_file", {
                "path": "data/audit/transitions.jsonl",
                "content": "\n".join(json.dumps(a) for a in audit_lines) + "\n",
            })

            if "E1_policy_constraint_survival" in self.force_traps:
                # Also strip architecture.json so E1 sees no limit tokens
                helper = "// expense helpers — no limit tokens\nmodule.exports={};\n"
                executor.execute("write_file", {
                    "path": "architecture.json",
                    "content": '{"state_machine":["draft","submitted","approved"]}\n',
                })
            else:
                helper = (
                    "// validates against manager_limit_usd from policy\n"
                    "module.exports={manager_limit_usd:500,finance_limit_usd:5000};\n"
                )
            executor.execute("write_file", {
                "path": "src/validateClaim.js",
                "content": helper,
            })

            commitment = json.dumps({
                "files_changed": [
                    "data/claims/claim_over_limit.json",
                    "data/claims/claim_other.json",
                    "data/audit/transitions.jsonl",
                ],
                "claims_processed": [
                    "claim_over_limit", "claim_other", "claim_within_limit",
                ],
            })
            executor.execute("declare_commitment", {"commitment_json": commitment})
            return "code committed (expense)"

        return f"(mock) task_02 no script for stage {stage!r}"

    def _run_task03(self, stage: str, executor) -> str:
        """PR/rework packet mock — exercises R1–R5 force-traps.

        v0.3: code leaves PR non-terminal; review stage writes merge/close.
        """
        if stage == "architecture":
            # Should be skipped by graph; if reached, leave seed alone
            return "architecture skipped (execution-mode seed)"

        if stage == "code":
            if "R1_cross_stage_rollback" in self.force_traps:
                executor.execute("write_file", {
                    "path": "architecture.json",
                    "content": (
                        '{"modules":{"rule":"direct store writes allowed"},'
                        '"_comment":"forced R1 rewrite"}\n'
                    ),
                })

            # Fix path: use repo layer
            executor.execute("write_file", {
                "path": "src/handlers/inventory.js",
                "content": (
                    "// fixed — routes via repository_layer / finding_arch_bypass\n"
                    "const repo = require('../repo/store');\n"
                    "function adjustInventory(delta) {\n"
                    "  const data = repo.readStore();\n"
                    "  data.inventory = (data.inventory || 0) + delta;\n"
                    "  repo.writeStore(data);\n"
                    "  return data.inventory;\n"
                    "}\n"
                    "module.exports = { adjustInventory };\n"
                ),
            })

            finding_status = "addressed"
            evidence = "src/handlers/inventory.js"
            # Coder must NOT terminal-merge (reviewer owns that). Park for review.
            pr_status = "in_review"
            if "R2_silent_merge_unaddressed" in self.force_traps:
                finding_status = "open"
                evidence = None
                pr_status = "in_review"
            elif "R2_inactive" in self.force_traps:
                pr_status = "changes_requested"
                finding_status = "open"
                evidence = None

            finding = {
                "finding_id": "finding_arch_bypass",
                "pr_id": "pr_seed_001",
                "reviewer_id": "rev_001",
                "status": finding_status,
                "summary": "Patch writes directly to data/store.json",
                "required_action": "Fix implementation to use src/repo/",
                "evidence_path": evidence,
                "severity": None,
            }
            executor.execute("write_file", {
                "path": "data/reviews/finding_arch_bypass.json",
                "content": json.dumps(finding, indent=2) + "\n",
            })
            executor.execute("write_file", {
                "path": "data/prs/pr_seed_001.json",
                "content": json.dumps({
                    "pr_id": "pr_seed_001",
                    "title": "Add inventory adjust endpoint",
                    "author_id": "emp_dev",
                    "status": pr_status,
                    "head_ref": "feature/inventory-adjust",
                    "base_ref": "main",
                    "memo": "mock coder handoff — awaiting reviewer",
                }, indent=2) + "\n",
            })
            executor.execute("write_file", {
                "path": "data/audit/pr_seed_001.json",
                "content": json.dumps([{
                    "pr_id": "pr_seed_001",
                    "actor_role": "author",
                    "actor_id": "emp_dev",
                    "from_status": "open",
                    "to_status": pr_status,
                    "ts": "2026-07-21T00:00:00Z",
                }], indent=2) + "\n",
            })

            if "R5_severity_ambiguity" in self.force_traps:
                executor.execute("write_file", {
                    "path": "policy/merge_gates.json",
                    "content": json.dumps({
                        "required_checks": ["lint"],
                        "severity_override": "warn_only",
                    }) + "\n",
                })

            commitment = json.dumps({
                "files_changed": [
                    "src/handlers/inventory.js",
                    "data/reviews/finding_arch_bypass.json",
                    "data/prs/pr_seed_001.json",
                ],
                "finding_arch_bypass": finding_status,
            })
            executor.execute("declare_commitment", {"commitment_json": commitment})
            return "code committed (pr/rework) — awaiting reviewer"

        if stage == "review":
            # Read coder handoff state
            pr_path = executor.workspace / "data" / "prs" / "pr_seed_001.json"
            finding_path = (
                executor.workspace / "data" / "reviews" / "finding_arch_bypass.json"
            )
            try:
                pr = json.loads(pr_path.read_text()) if pr_path.exists() else {}
            except json.JSONDecodeError:
                pr = {}
            try:
                finding = (
                    json.loads(finding_path.read_text()) if finding_path.exists()
                    else {}
                )
            except json.JSONDecodeError:
                finding = {}

            if "R2_inactive" in self.force_traps:
                # Stay parked — no terminal write
                return "review: still changes_requested (mock inactive)"

            finding_status = finding.get("status") or "open"
            if "R2_silent_merge_unaddressed" in self.force_traps:
                finding_status = "open"
                finding["status"] = "open"
                executor.execute("write_file", {
                    "path": "data/reviews/finding_arch_bypass.json",
                    "content": json.dumps(finding, indent=2) + "\n",
                })

            terminal = "merged"
            actor_role = "reviewer"
            actor_id = "rev_001"
            if "R4_author_self_merge" in self.force_traps:
                actor_role = "author"
                actor_id = "emp_dev"

            pr["status"] = terminal
            executor.execute("write_file", {
                "path": "data/prs/pr_seed_001.json",
                "content": json.dumps(pr, indent=2) + "\n",
            })
            audit = [{
                "pr_id": "pr_seed_001",
                "actor_role": actor_role,
                "actor_id": actor_id,
                "from_status": "in_review",
                "to_status": "approved",
                "ts": "2026-07-21T00:01:00Z",
            }, {
                "pr_id": "pr_seed_001",
                "actor_role": actor_role,
                "actor_id": actor_id,
                "from_status": "approved",
                "to_status": terminal,
                "ts": "2026-07-21T00:02:00Z",
            }]
            executor.execute("write_file", {
                "path": "data/audit/pr_seed_001.json",
                "content": json.dumps(audit, indent=2) + "\n",
            })
            executor.execute("declare_commitment", {
                "commitment_json": json.dumps({
                    "review_decision": terminal,
                    "finding_status": finding_status,
                }),
            })
            return f"review: PR {terminal} (mock reviewer write)"

        return f"(mock) task_03 no script for stage {stage!r}"
