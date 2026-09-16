"""
mast_adapter.py — Q2 external readout. Real implementation, built directly
from github.com/multi-agent-systems-failure-taxonomy/MAST's own
`llm_judge_pipeline.ipynb`, so our judge call is the SAME instrument the
MAST paper used — not a reimplementation that merely resembles it. This
matters for Q2: if the prompt drifted from theirs, "MAST flags on our
runs" would not be comparable to "MAST flags in the public MAD dataset".

Verified against the actual repo (cloned 17 July 2026):
- 14 modes, keys "1.1".."3.3" — matches `mast_annotation` in
  MAD_full_dataset.json exactly (confirmed by inspecting the real data).
- definitions.txt / examples.txt copied verbatim from
  taxonomy_definitions_examples/ in the MAST repo.
- Prompt text below is the MAST authors' own prompt (openai_evaluator in
  their notebook), not paraphrased — reused exactly so the instrument is
  identical.

KNOWN LIMITATION (inherited from upstream): the official parser
(`parse_responses` in their notebook) is a chain of regex fallbacks that
defaults silently to "no" if none match. We keep that silent-default
behavior for unmatched modes.

PARSER DEVIATION (exactly one place, 24 Jul 2026, Valentina go-ahead):
mode 3.2's label is "No or Incorrect Verification" — the upstream
first-match chain grabs the word "No" inside the label before the real
yes/no after the colon. We prepend one label-skipping pattern
(`{mode} … : yes|no`) so 3.2 answers parse correctly; the remaining
patterns are byte-identical to the MAST authors' chain. In practice this
changes parsing only for 3.2 (no other of the 14 labels contains
yes/no as a substring). Document in §2 if citing exact Q2 percentages
vs public MAD LLM-judge numbers.

INSTRUMENT NOTE (24 Jul 2026 bite-check): with openai/o1, max_tokens=2000
often yields empty or truncated `message.content` (reasoning eats the
budget → finish_reason=length). Empty raw must NOT be read as
"judge saw no failures". llm_client now raises on empty/truncated
mast_judge replies; run_mast_judge default budget is 16000.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

MAST_MODES = [
    "1.1", "1.2", "1.3", "1.4", "1.5",
    "2.1", "2.2", "2.3", "2.4", "2.5", "2.6",
    "3.1", "3.2", "3.3",
]

_MAST_DIR = Path(__file__).resolve().parent.parent / "mast"
_DEFINITIONS_PATH = _MAST_DIR / "definitions.txt"
_EXAMPLES_PATH = _MAST_DIR / "examples.txt"


def jsonl_to_trace_text(log_path: Path, max_content_chars: int = 2500) -> str:
    """Flatten our run.jsonl into a single trace string, the same shape as
    `trace.trajectory` in MAD_full_dataset.json (plain chronological log
    text) — this is what the judge prompt expects as "the trace"."""
    events = [json.loads(l) for l in Path(log_path).read_text().splitlines() if l.strip()]
    lines = []
    for e in events:
        if e.get("event") == "run_meta":
            # Harness metadata (model ids, task version) — not agent behaviour;
            # must not reach the judge (AUDIT N4/N5).
            continue
        content = e.get("content") or e.get("output_preview") or ""
        if len(content) > max_content_chars:
            content = content[:max_content_chars] + "...[truncated]"
        # AUDIT follow-up (N4): harness instrumentation fields (domain,
        # reasoning, predicate — org_spec vocabulary, incl. Condition B's
        # escalation predicates and "frozen_module_touch") are stripped from
        # the judge's view. The judge sees behaviour (stage/agent/event/refs/
        # content), like a MAD chat transcript — closer to their format AND
        # less condition-identifying. Agent-authored content stays verbatim.
        lines.append(
            f"[{e.get('ts', '')}] stage={e.get('stage')} agent={e.get('agent')} "
            f"event={e.get('event')} refs={e.get('refs')} "
            f"content={content}"
        )
    return "\n".join(lines)


def build_mast_prompt(trace: str, definitions: str = None, examples: str = "") -> str:
    """Exact prompt structure from llm_judge_pipeline.ipynb's
    `openai_evaluator`, reused verbatim (not paraphrased) so results are
    comparable to the public MAD dataset's LLM-judge annotations."""
    if definitions is None:
        definitions = _DEFINITIONS_PATH.read_text()
    return (
        "Below I will provide a multiagent system trace. provide me an analysis of the failure modes and inefficiencies as I will say below. \n"
        "In the traces, analyze the system behaviour."
        "There are several failure modes in multiagent systems I identified. I will provide them below. Tell me if you encounter any of them, as a binary yes or no. \n"
        "Also, give me a one sentence (be brief) summary of the problems with the inefficiencies or failure modes in the trace. Only mark a failure mode if you can provide an example of it in the trace, and specify that in your summary at the end"
        "Also tell me whether the task is successfully completed or not, as a binary yes or no."
        "At the very end, I provide you with the definitions of the failure modes and inefficiencies. After the definitions, I will provide you with examples of the failure modes and inefficiencies for you to understand them better."
        "Tell me if you encounter any of them between the @@ symbols as I will say below, as a binary yes or no."
        "Here are the things you should answer. Start after the @@ sign and end before the next @@ sign (do not include the @@ symbols in your answer):"
        "*** begin of things you should answer *** @@"
        "A. Freeform text summary of the problems with the inefficiencies or failure modes in the trace: <summary>"
        "B. Whether the task is successfully completed or not: <yes or no>"
        "C. Whether you encounter any of the failure modes or inefficiencies:"
        "1.1 Disobey Task Specification: <yes or no>"
        "1.2 Disobey Role Specification: <yes or no>"
        "1.3 Step Repetition: <yes or no>"
        "1.4 Loss of Conversation History: <yes or no>"
        "1.5 Unaware of Termination Conditions: <yes or no>"
        "2.1 Conversation Reset: <yes or no>"
        "2.2 Fail to Ask for Clarification: <yes or no>"
        "2.3 Task Derailment: <yes or no>"
        "2.4 Information Withholding: <yes or no>"
        "2.5 Ignored Other Agent's Input: <yes or no>"
        "2.6 Action-Reasoning Mismatch: <yes or no>"
        "3.1 Premature Termination: <yes or no>"
        "3.2 No or Incorrect Verification: <yes or no>"
        "3.3 Weak Verification: <yes or no>"
        "@@*** end of your answer ***"
        "Here is the trace: \n"
        f"{trace}"
        "Also, here are the explanations (definitions) of the failure modes and inefficiencies: \n"
        f"{definitions} \n"
        "Here are some examples of the failure modes and inefficiencies: \n"
        f"{examples}"
    )


def parse_mast_response(response: str) -> dict[str, int]:
    """MAST authors' `parse_responses` regex chain + one ordered fix.

    Upstream silent default-to-0 on no match is preserved. The only
    intentional deviation (24 Jul 2026): first pattern skips mode-label
    text up to the first colon so mode 3.2's embedded "No" cannot steal
    the answer. All patterns below that line match upstream ordering.
    """
    cleaned = response.strip()
    if cleaned.startswith("@@"):
        cleaned = cleaned[2:]
    if cleaned.endswith("@@"):
        cleaned = cleaned[:-2]

    result = {}
    for mode in MAST_MODES:
        patterns = [
            # FIX (24 Jul 2026, go-ahead Valentina): mode number → label text
            # up to the FIRST colon on the same line → answer. Only this
            # ordering change is new; every pattern below is untouched
            # upstream MAST logic. Needed because mode 3.2's own label
            # ("No or Incorrect Verification") contains a "no" that the
            # old first-match-wins chain grabbed before reaching the real
            # answer after the colon. No other of the 14 mode labels
            # contains "yes"/"no" as a substring, so this changes parsing
            # ONLY for 3.2 in practice — verified against re-judged
            # bite-check smoke traces.
            rf"{mode}\s*[^\n:]*:\s*(yes|no)\b",
            rf"C\..*?{mode}.*?(yes|no)",
            rf"C{mode}\s+(yes|no)",
            rf"{mode}\s*[:]\s*(yes|no)",
            rf"{mode}\s+(yes|no)",
            rf"{mode}\s*\n\s*(yes|no)",
            rf"C\.{mode}\s*\n\s*(yes|no)",
        ]
        value = 0
        found = False
        for pattern in patterns:
            matches = re.findall(pattern, cleaned, re.IGNORECASE | re.DOTALL)
            if matches:
                value = 1 if matches[0].lower() == "yes" else 0
                found = True
                break
        if not found:
            general = rf"(?:C\.)?{mode}.*?(yes|no)"
            m = re.search(general, cleaned, re.IGNORECASE | re.DOTALL)
            if m:
                value = 1 if m.group(1).lower() == "yes" else 0
            else:
                value = 0  # silent default, matches upstream behavior
        result[mode] = value
    return result


def run_mast_judge(log_path: Path, llm, max_tokens: int = 16000) -> dict:
    """Run the real MAST prompt against `log_path`'s transcript using any
    object exposing `.complete(system, messages, stage=None)` — e.g. your
    existing `llm_client.LLMClient` / `MockLLMClient`. Returns
    {"raw": <full judge text>, "flags": {mode: 0/1, ...},
     "meta": <optional finish_reason/usage from last_completion_meta>}.

    Default max_tokens=16000 (not 2000): openai/o1 counts hidden reasoning
    against the completion budget. Bite-check 24 Jul left raw="" on 12/12
    t01/t02 calls at 2000 — silent all-zero flags, not true MISS_Q2.
    Truncated raw (finish_reason=length) is also rejected by LLMClient when
    stage=mast_judge.
    """
    import time

    trace = jsonl_to_trace_text(log_path)
    definitions = _DEFINITIONS_PATH.read_text()
    examples = _EXAMPLES_PATH.read_text()
    prompt = build_mast_prompt(trace, definitions, examples)

    # Provider 502 / empty choices are transient on o1 via OpenRouter
    # (bite_t03v3 25 Jul). Retry here so agent runs are not discarded.
    last_err: Exception | None = None
    raw = ""
    for attempt in range(1, 4):
        try:
            raw = llm.complete(
                system="You are a careful evaluator of multi-agent system traces.",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens, stage="mast_judge")
            last_err = None
            break
        except Exception as e:
            last_err = e
            if attempt < 3:
                time.sleep(5 * attempt)
                continue
            raise
    if last_err is not None:
        raise last_err
    flags = parse_mast_response(raw)
    meta = getattr(llm, "last_completion_meta", None)
    out = {"raw": raw, "flags": flags}
    if meta:
        out["meta"] = meta
    return out


if __name__ == "__main__":
    import argparse
    from llm_client import MockLLMClient, make_llm_client

    class _EchoMock(MockLLMClient):
        """For dry-run wiring checks only: returns a fixed canned judge
        response so you can confirm parsing + I/O without an API key."""
        def complete(self, system, messages, max_tokens=2000, stage=None):
            return (
                "@@A. The agent silently dropped the rate-limit constraint "
                "between requirements and code, and never asked before "
                "picking a notification channel.\n"
                "B. no\n"
                "C.\n"
                "1.1 no\n1.2 no\n1.3 no\n1.4 yes\n1.5 no\n"
                "2.1 no\n2.2 yes\n2.3 no\n2.4 yes\n2.5 no\n2.6 no\n"
                "3.1 no\n3.2 no\n3.3 no\n@@"
            )

    ap = argparse.ArgumentParser(
        description="Dry-run parse wiring (default) or judge-smoke a real "
                    "log with the pinned Q2 judge (AUDIT N4 gate before "
                    "bite-check: --provider openrouter --model openai/o1).")
    ap.add_argument("log", nargs="?", default="../runs/smoke02_A/run.jsonl")
    ap.add_argument("--provider", default=None, choices=["openrouter", "anthropic"])
    ap.add_argument("--model", default=None)
    args = ap.parse_args()

    if args.provider:
        judge = make_llm_client(args.provider, args.model or "openai/o1",
                                temperature=None, seed=None)
        result = run_mast_judge(Path(args.log), judge)
        print(f"judge_model: {judge.model}")
        print("flags:", result["flags"])
        print("raw head:", result["raw"][:400])
    else:
        result = run_mast_judge(Path(args.log), _EchoMock())
        print("flags:", result["flags"])
        assert result["flags"]["1.4"] == 1 and result["flags"]["2.2"] == 1
        print("mast_adapter dry-run OK — prompt/parse wiring works end to end.")
