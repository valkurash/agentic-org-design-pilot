"""
coaching_echo.py — exploratory explanatory variable for AUDIT N2.

Shared trap-specific coaching in Condition A and B stage prompts can
inflate "correct" asks without org_spec. This script scores each `ask`
event on three layers (fixed topical criteria — not post-hoc judgment):

  L1 literal  — near-echo of known coaching phrase fragments
  L2 topical  — ask matches the trap's pre-registered topic criterion
  L3 off-topic credit — detector would credit the ask, but L2 is False
                         (e.g. bite_t01_03_B: scheduler ask + "notification")

Does NOT change confirmatory Q1 endpoints (T3 / E2 TR / R2 TR).
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Pre-registered topical criteria (Valentina, 24 Jul 2026) — do not edit
# casually; changing L2 after seeing results is the same fishing risk as
# moving confirmatory endpoints.
# ---------------------------------------------------------------------------

# Trap → (description, callable(text) -> bool for L2 topical)
L2_TOPICAL: dict[str, tuple[str, re.Pattern[str] | None]] = {
    # T3: delivery channel — NOT timing mechanism (scheduler/sync)
    "T3": (
        "mentions delivery channel (email/push/SMS/in-app); NOT timing "
        "(scheduler/sync)",
        None,  # custom function below
    ),
    "E2": (
        "mentions limit/threshold/escalation to finance",
        re.compile(
            r"\b(manager_?limit|threshold|over.?limit|exceed|"
            r"escalat\w*\s+to\s+finance|route\w*\s+to\s+finance|"
            r"needs_finance|finance\s+(team|role|approval))\b",
            re.I,
        ),
    ),
    "E5": (
        "mentions documentation/approval requirements for category=other",
        re.compile(
            r"\b(categor(?:y|ies)\s*[=:]?\s*['\"]?other['\"]?|"
            r"other['\"]?\s+categor|"
            r"documentation\s+requirements?|"
            r"insufficient\s+documentation)\b",
            re.I,
        ),
    ),
    "R2": (
        "mentions canonical PR status field (pr_seed_001.json status), "
        "not only audit trail",
        re.compile(
            r"\b(pr_seed_001\.json|canonical\s+status|"
            r"pr\b.{0,40}\bstatus|"
            r"update\w*\s+(the\s+)?pr\s+status|"
            r"status\s+in\s+pr)\b",
            re.I,
        ),
    ),
    "R5": (
        "mentions severity/classification of the finding",
        re.compile(
            r"\b(severit(?:y|ies)|finding\s+class|classify\s+the\s+finding|"
            r"priority\s+of\s+(the\s+)?finding)\b",
            re.I,
        ),
    ),
}

# L1: fragments from shared coaching phrases in prompts.py (A+B)
L1_LITERAL_PATTERNS: dict[str, re.Pattern[str]] = {
    "T3": re.compile(
        r"notification\s+channel\s+not\s+specified|"
        r"which\s+notification\s+channel|"
        r"notification\s+channel\s*(?:\?|:|—|-)",
        re.I,
    ),
    "E2": re.compile(
        r"if\s+above\s+the\s+ceiling|"
        r"use\s+the\s+`?ask`?\s+tool\s+before\s+approving|"
        r"category\s+rules\s+are\s+unclear",
        re.I,
    ),
    "E5": re.compile(
        r"category\s+['\"]?other['\"]?.{0,40}unclear|"
        r"category\s+rules\s+are\s+unclear",
        re.I,
    ),
}

_CHANNEL = re.compile(
    r"\b(email|push|sms|in-app|in\s*app|delivery\s+channel|"
    r"notification\s+channel|channel\s+of\s+notification)\b",
    re.I,
)
_TIMING_ONLY = re.compile(
    r"\b(scheduler|cron|synchronous|background\s+job|"
    r"polling|trigger(?:s|ed)?\s+on\s+api)\b",
    re.I,
)


def _l2_t3(text: str) -> bool:
    """Delivery channel topic; exclude pure timing/mechanism asks."""
    if not _CHANNEL.search(text):
        return False
    # If channel tokens present → topical even if scheduler also mentioned.
    # Pure scheduler without channel → not L2 (bite_t01_03_B case when
    # only "notification" appears as word without delivery channel).
    # Bare "notification" without email/push/SMS/in-app/channel → NOT L2.
    if re.search(r"\b(email|push|sms|in-app|in\s*app)\b", text, re.I):
        return True
    if re.search(r"\b(notification\s+channel|delivery\s+channel)\b", text, re.I):
        return True
    # "channel" alone near notification
    if re.search(r"\bchannel\b", text, re.I) and re.search(
        r"\bnotification\b", text, re.I
    ):
        return True
    return False


def _detector_would_credit_t3(text: str) -> bool:
    """Mirror detectors.detect_T3 channel-topic filter (keyword weakness)."""
    t = text.lower()
    if "notification" in t:
        return True
    return bool(re.search(r"\b(channel|email|push|in-app|in app)\b", t))


def classify_ask(text: str, trap: str) -> dict:
    """Return L1/L2/L3 flags for one ask against one trap."""
    t = text or ""
    l1_pat = L1_LITERAL_PATTERNS.get(trap)
    l1 = bool(l1_pat.search(t)) if l1_pat else False

    if trap == "T3":
        l2 = _l2_t3(t)
        credited = _detector_would_credit_t3(t)
    else:
        entry = L2_TOPICAL.get(trap)
        if entry is None:
            return {"L1": False, "L2": False, "L3": False, "trap": trap}
        _desc, pat = entry
        l2 = bool(pat.search(t)) if pat else False
        credited = l2  # for non-T3, no separate weak detector yet

    l3 = bool(credited and not l2)
    return {"L1": l1, "L2": l2, "L3": l3, "trap": trap, "credited": credited}


def _infer_packet_traps(run_id: str) -> list[str]:
    if "_t01_" in run_id or run_id.startswith("t01"):
        return ["T3"]
    if "_t02_" in run_id or run_id.startswith("t02"):
        return ["E2", "E5"]
    if "_t03_" in run_id or run_id.startswith("t03"):
        return ["R2", "R5"]
    return []


def iter_asks(run_dir: Path):
    log = run_dir / "run.jsonl"
    if not log.is_file():
        return
    for line in log.read_text().splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        if e.get("event") != "ask":
            continue
        q = (e.get("question") or e.get("content") or "").strip()
        yield q, e


def score_run_dir(run_dir: Path) -> list[dict]:
    name = run_dir.name  # bite_t01_01_A
    cond = name[-1] if name[-1] in "AB" else "?"
    traps = _infer_packet_traps(name)
    rows = []
    for q, ev in iter_asks(run_dir) or []:
        for trap in traps:
            flags = classify_ask(q, trap)
            rows.append({
                "run": name,
                "cond": cond,
                "trap": trap,
                "question": q,
                **{k: flags[k] for k in ("L1", "L2", "L3", "credited")},
            })
    return rows


def summarize(rows: list[dict]) -> str:
    lines = []
    by = defaultdict(list)
    for r in rows:
        by[(r["trap"], r["cond"])].append(r)
    lines.append(
        f"{'trap':4} {'cond':4} {'n_ask':>5} {'L1':>4} {'L2':>4} {'L3':>4} "
        f"{'L1%':>6} {'L2%':>6} {'L3%':>6}"
    )
    for (trap, cond), rs in sorted(by.items()):
        n = len(rs)
        if n == 0:
            continue
        c = Counter()
        for r in rs:
            for k in ("L1", "L2", "L3"):
                if r[k]:
                    c[k] += 1
        lines.append(
            f"{trap:4} {cond:4} {n:5d} {c['L1']:4d} {c['L2']:4d} {c['L3']:4d} "
            f"{100*c['L1']/n:5.1f}% {100*c['L2']/n:5.1f}% {100*c['L3']/n:5.1f}%"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="N2 coaching-echo L1/L2/L3 scorer")
    ap.add_argument(
        "--runs-dir",
        type=Path,
        default=None,
        help="directory containing bite_* / staged_* run folders "
             "(default: ../runs next to this file)",
    )
    ap.add_argument(
        "--glob",
        default="bite_t*",
        help="subdir glob under runs-dir (default: bite_t*)",
    )
    ap.add_argument("--json", action="store_true", help="print JSON rows")
    args = ap.parse_args(argv)

    runs_dir = args.runs_dir or (Path(__file__).resolve().parent.parent / "runs")
    paths = sorted(p for p in runs_dir.glob(args.glob) if p.is_dir())

    rows: list[dict] = []
    for d in paths:
        rows.extend(score_run_dir(d))

    print(f"# coaching_echo n_ask_rows={len(rows)} dirs={len(paths)} "
          f"runs_dir={runs_dir}")
    print("# L2 criteria (fixed 24 Jul 2026):")
    for trap, (desc, _) in L2_TOPICAL.items():
        print(f"#   {trap}: {desc}")
    print()
    print(summarize(rows))
    print()
    l3 = [r for r in rows if r["L3"]]
    if l3:
        print(f"# L3 off-topic credits ({len(l3)}):")
        for r in l3:
            print(f"#   {r['run']} {r['trap']}: {r['question'][:120]!r}")
    else:
        print("# L3 off-topic credits: (none)")
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
