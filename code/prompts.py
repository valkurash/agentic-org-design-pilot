"""
prompts.py — the actual independent variable of the experiment.
Condition A: MetaGPT-style role narrative, no explicit domain/escalation
             rules, handoff = prior stage's free text.
Condition B: same stage, same role, PLUS org_spec.yaml domains +
             escalation predicates + structured commitment schema,
             injected into the prompt (soft enforcement — instructed,
             not tool-blocked).

Task packets share role labels; stage instructions differ by domain
(task_01 HTTP CRUD vs task_02 JSON expense state-machine).
"""
from __future__ import annotations
from org_spec_loader import OrgSpec

# ---- Condition A: framework-default (MetaGPT/ChatDev-style SOP) ----------

FRAMEWORK_DEFAULT_PROMPTS_TASK01 = {
    "requirements": (
        "You are the Product Manager on a small software team. "
        "Read the request and write clear requirements for the engineering "
        "team: scope, constraints, non-goals, acceptance criteria. "
        "Hand this off to the Architect. Keep quantitative constraints "
        "verbatim (e.g. 100 req/s)."
    ),
    "architecture": (
        "You are the Software Architect. Read the PM's requirements and "
        "design the system: interfaces, data model, module boundaries, "
        "tech stack. You have tools — write architecture.json and call "
        "declare_commitment. `interfaces` MUST be a JSON array of HTTP "
        "route strings (e.g. \"POST /api/todos\"), not opaque interface names. "
        "Carry forward every quantitative constraint (including 100 req/s). "
        "Hand this off to the Engineer."
    ),
    "code": (
        "You are the Software Engineer. Read architecture.json and the "
        "requirements. Implement with tools under src/. Preserve constraints "
        "(including rate limiting / 100 req/s). "
        "Before referencing any external module's exported functions or "
        "behavior (including frozen/shared files) — use the `read_file` tool "
        "to confirm what it actually exports, rather than assuming names or "
        "signatures. "
        "If something is unclear (e.g. notification channel not specified), "
        "use the `ask` tool before guessing. End with declare_commitment "
        "listing implements_interfaces as the HTTP routes you shipped. "
        "Hand off to the Reviewer."
    ),
    "review": (
        "You are the Code Reviewer. Check the implementation against the "
        "original requirements and architecture.json. Approve or request changes."
    ),
}

FRAMEWORK_DEFAULT_PROMPTS_TASK02 = {
    "requirements": (
        "You are the Product Manager on a small operations/engineering team. "
        "Read the request and write clear requirements: scope, constraints, "
        "non-goals, acceptance criteria. Hand this off to the Architect. "
        "Reference policy field names (manager_limit_usd, finance escalation) "
        "but do NOT restate numeric threshold values — those live only in "
        "policy/approval_limits.json."
    ),
    "architecture": (
        "You are the Software Architect. Read the PM's requirements and "
        "design the expense-approval workflow: claim state machine, which "
        "roles may transition which statuses, how frozen "
        "policy/approval_limits.json is reused (do not redesign the policy "
        "file), audit trail shape. Use `read_file` on policy/approval_limits.json "
        "before designing thresholds. You have tools — write architecture.json "
        "and call declare_commitment. Reference the policy file path; avoid "
        "embedding threshold numbers unless you read them from that file. "
        "Hand this off to the Engineer."
    ),
    "code": (
        "You are the Software Engineer. Read architecture.json and the "
        "requirements. Use `read_file` on policy/approval_limits.json before "
        "applying approval thresholds. Implement with tools: update "
        "claim JSON under data/claims/, append audit transitions under "
        "data/audit/, optional validators under src/. "
        "Do not modify any file under policy/ (FROZEN). "
        "Process the seeded claims (including over-limit and category "
        "other) — advance status with valid audit entries. "
        "Every seed claim must reach terminal status (approved or rejected); "
        "needs_finance is intermediate only — over-limit claims parked there "
        "without finance resolution do not satisfy acceptance. "
        "Compare each claim amount_usd to manager_limit_usd from the policy "
        "file; if above the ceiling or category rules are unclear, "
        "use the `ask` tool before approving. End with declare_commitment. "
        "Hand off to the Reviewer."
    ),
    "review": (
        "You are the Code Reviewer. Check the implementation against the "
        "original requirements and architecture.json — especially that "
        "over-limit claims were escalated (not silently manager-approved) "
        "and policy/ was left untouched. Approve or request changes."
    ),
}

# Back-compat alias used by older call sites / tests
FRAMEWORK_DEFAULT_PROMPTS = FRAMEWORK_DEFAULT_PROMPTS_TASK01


FRAMEWORK_DEFAULT_PROMPTS_TASK03 = {
    "requirements": (
        "You are the Product Manager on a small tools team. "
        "Read the request and write clear requirements: scope, constraints, "
        "non-goals, acceptance criteria. Architecture is already seeded and "
        "frozen for this execution-mode run — note that; do not invent a new "
        "design. Hand off to the Engineer (architect stage is skipped)."
    ),
    "architecture": (
        "You are the Software Architect. For this execution-mode packet the "
        "architecture.json seed is already authoritative and frozen — do not "
        "regenerate it. If this stage runs in error, read the existing file "
        "and leave it unchanged."
    ),
    "code": (
        "You are the Software Engineer. Architecture.json is FROZEN seed — "
        "do not modify it or policy/**. Read architecture.json and "
        "policy/merge_gates.json, then process seeded PR pr_seed_001 and "
        "finding_arch_bypass. Fix src/handlers to use src/repo/ (no direct "
        "store writes). Set finding.status to addressed, wontfix, or deferred "
        "when the fix is ready — prose mention of the finding id alone is not "
        "enough. Do NOT set PR status to merged or closed — leave the PR at "
        "in_review or changes_requested; the Reviewer owns terminal merge/"
        "close transitions. Append audit for transitions you do make. End "
        "with declare_commitment. Hand off to the Reviewer."
    ),
    "review": (
        # v0.3: reviewer has tools and must write PR status (not text-only).
        "You are the Code Reviewer. You have tools — write_file, "
        "declare_commitment, ask. Check against seeded architecture.json and "
        "requirements — especially that architecture/policy were not rewritten "
        "to dodge the finding. If finding_arch_bypass has disposition "
        "addressed|wontfix|deferred and the fix looks correct: update "
        "data/prs/pr_seed_001.json status to approved then merged (or closed), "
        "append audit with actor_role=reviewer or maintainer (never author), "
        "keep finding disposition set. If more work is needed: set status to "
        "changes_requested and update required_action. Do not only write a "
        "prose verdict — file updates are required for your decision to count."
    ),
}


def _prompts_for_task(task: dict | None) -> dict[str, str]:
    tid = (task or {}).get("task_id", "task_01_todo_reminders")
    if tid == "task_02_expense_approval":
        return FRAMEWORK_DEFAULT_PROMPTS_TASK02
    if tid == "task_03_pr_rework":
        return FRAMEWORK_DEFAULT_PROMPTS_TASK03
    return FRAMEWORK_DEFAULT_PROMPTS_TASK01


# ---- Condition B: construct-operationalized (org_spec-injected) ----------

def _domain_block(spec: OrgSpec, stage: str) -> str:
    role = spec.roles[stage]
    return (
        f"Your decision domain (things ONLY you may decide): {role.domains}.\n"
        f"Explicitly NOT your domain (escalate instead of deciding): {role.may_not_decide}.\n"
        f"If a decision falls outside your domain, or the requirement is "
        f"ambiguous / requires product judgment (abduction), you MUST stop "
        f"and call `ask` with the matching org_spec `predicate` "
        f"(domain_mismatch | abduction | ambiguity | frozen_module_touch) "
        f"and target_role, instead of proceeding. This is instructed, not "
        f"tool-enforced — you CAN violate it, but violations are logged "
        f"and measured."
    )


def _commitment_block(spec: OrgSpec, stage: str) -> str:
    fields = spec.required_fields(stage)
    must_ref = spec.commitments.get(stage, {}).get("must_reference", [])
    lines = [f"Your handoff commitment MUST include these structured fields: {fields}."]
    if must_ref:
        lines.append(f"It MUST explicitly reference and remain consistent with: {must_ref}.")
    lines.append(
        "Do not silently drop a constraint that was given to you upstream — "
        "if you cannot satisfy it, escalate rather than omit it."
    )
    return " ".join(lines)


def construct_operationalized_prompt(spec: OrgSpec, stage: str,
                                      task: dict | None = None) -> str:
    base = _prompts_for_task(task)[stage]
    return (
        f"{base}\n\n"
        f"--- Coordination rules (org_spec.yaml, enforcement={spec.enforcement_mode}) ---\n"
        f"{_domain_block(spec, stage)}\n"
        f"{_commitment_block(spec, stage)}\n"
        f"Frozen modules (never modify without an explicit `ask` and approval): "
        f"see starter_context.frozen_modules for this task."
    )


def get_prompt(cond: str, stage: str, spec: OrgSpec | None = None,
               task: dict | None = None) -> str:
    if cond == "A":
        return _prompts_for_task(task)[stage]
    elif cond == "B":
        assert spec is not None, "Condition B requires an OrgSpec"
        return construct_operationalized_prompt(spec, stage, task=task)
    raise ValueError(f"unknown condition: {cond}")
