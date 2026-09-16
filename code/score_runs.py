#!/usr/bin/env python3
"""
score_runs.py — batch Q1 detector scorer over run directories (AUDIT follow-up).

Before this script the only batch scorer was fabrication_desync.py (task_03
exploratory); Q1 detector results existed only as per-run stdout at run time.
Full N (~180 runs) needs a single reproducible table for draft §4.

Task packet is resolved per run dir: run_meta event (task_id) if present
(runs after 22 Jul 2026), else by directory-name convention
(pilot_pair_* → task_01, pilot_t02_* → task_02, pilot_t03_* → task_03).

Baselines: task_02/03 from fixtures dirs; task_01 by materializing the
CURRENT packet epoch into a temp dir. NOTE: historical task_01 pilots from
earlier packet epochs (pre-v0.5 middleware.py era) may mismatch the current
baseline — the runs/README ledger stays authoritative for those; this script
is for current-epoch runs (bite-check, staged N, full N).

Usage:
  python score_runs.py --batch '../runs/pilot_t03_*'
  python score_runs.py --batch '../runs/full_*' --csv ../runs/full_scores.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import tempfile
from pathlib import Path

_STAND = Path(__file__).resolve().parent
sys.path.insert(0, str(_STAND))

from detectors import run_all_detectors, snapshot_hashes  # noqa: E402
from org_spec_loader import load_task  # noqa: E402
from run_pair import (  # noqa: E402
    materialize_starter_context, read_architecture_and_routes,
)

_TASKS_DIR = _STAND.parent / "tasks"
_TASK_FILES = {
    "task_01_todo_reminders": _TASKS_DIR / "task_01_todo_reminders.yaml",
    "task_02_expense_approval": _TASKS_DIR / "task_02_expense_approval.yaml",
    "task_03_pr_rework": _TASKS_DIR / "task_03_pr_rework.yaml",
}
_DIR_PREFIX_TASK = {
    "pilot_pair": "task_01_todo_reminders",
    "pilot_t02": "task_02_expense_approval",
    "pilot_t03": "task_03_pr_rework",
    "full_t01": "task_01_todo_reminders",
    "full_t02": "task_02_expense_approval",
    "full_t03": "task_03_pr_rework",
    "bite_t01": "task_01_todo_reminders",
    "bite_t02": "task_02_expense_approval",
    "bite_t03": "task_03_pr_rework",
}


def _find_log(run_dir: Path) -> Path | None:
    preferred = run_dir / "run.jsonl"
    if preferred.exists():
        return preferred
    matches = sorted(run_dir.glob("run*.jsonl"))
    return matches[0] if matches else None


def _task_id_for(run_dir: Path, log_path: Path) -> str | None:
    # 1) run_meta event (runs ≥ 22 Jul 2026)
    try:
        for line in log_path.read_text().splitlines():
            if not line.strip():
                continue
            e = json.loads(line)
            if e.get("event") == "run_meta":
                meta = json.loads(e.get("content") or "{}")
                if meta.get("task_id"):
                    return meta["task_id"]
            break  # run_meta is the first event when present
    except (json.JSONDecodeError, OSError):
        pass
    # 2) directory-name convention
    name = run_dir.name
    for prefix, tid in _DIR_PREFIX_TASK.items():
        if name.startswith(prefix):
            return tid
    return None


class _Baselines:
    """Lazy per-task baseline hashes (fixtures / current-epoch materialize)."""

    def __init__(self):
        self._cache: dict[str, dict[str, str]] = {}
        self._tmp: tempfile.TemporaryDirectory | None = None

    def for_task(self, task_id: str, task: dict) -> dict[str, str]:
        if task_id in self._cache:
            return self._cache[task_id]
        if task_id == "task_02_expense_approval":
            base = snapshot_hashes(_TASKS_DIR / "fixtures_task_02")
        elif task_id == "task_03_pr_rework":
            base = snapshot_hashes(_TASKS_DIR / "fixtures_task_03")
        else:
            self._tmp = self._tmp or tempfile.TemporaryDirectory()
            ws = Path(self._tmp.name) / task_id
            materialize_starter_context(ws, task)
            base = snapshot_hashes(ws)
        self._cache[task_id] = base
        return base


def score_dir(run_dir: Path, tasks: dict, baselines: _Baselines) -> dict | None:
    log_path = _find_log(run_dir)
    if log_path is None:
        print(f"skip (no run*.jsonl): {run_dir}", file=sys.stderr)
        return None
    task_id = _task_id_for(run_dir, log_path)
    if task_id is None or task_id not in tasks:
        print(f"skip (unknown task): {run_dir}", file=sys.stderr)
        return None
    task = tasks[task_id]
    workspace = run_dir / "workspace"
    kwargs = {}
    if task_id == "task_01_todo_reminders":
        arch, routes, src = read_architecture_and_routes(workspace, log_path)
        kwargs = {"architecture_json": arch, "implemented_routes": routes,
                  "routes_source": src}
    results = run_all_detectors(
        workspace, log_path, task,
        baselines.for_task(task_id, task), **kwargs)
    cond = "A" if run_dir.name.endswith("_A") else (
        "B" if run_dir.name.endswith("_B") else "?")
    row = {"run": run_dir.name, "task": task_id, "cond": cond}
    for r in results:
        row[r.trap_id] = r.status
    row["_details"] = {r.trap_id: r.detail for r in results}
    return row


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="batch Q1 detector scorer")
    ap.add_argument("--batch", nargs="+", required=True, metavar="GLOB",
                    help="glob(s) of run dirs, e.g. '../runs/pilot_t03_*'")
    ap.add_argument("--csv", type=Path, default=None,
                    help="also write rows to CSV (detector statuses only)")
    ap.add_argument("--details", action="store_true",
                    help="print per-trap detail lines")
    args = ap.parse_args(argv)

    dirs: list[Path] = []
    for pat in args.batch:
        p = Path(pat)
        dirs.extend(sorted(p.parent.glob(p.name)) if "/" in pat
                    else sorted(Path().glob(pat)))
    dirs = [d for d in dirs if d.is_dir()]
    if not dirs:
        ap.error("no run dirs matched")

    tasks = {tid: load_task(path) for tid, path in _TASK_FILES.items()
             if path.exists()}
    baselines = _Baselines()

    rows = [r for d in dirs if (r := score_dir(d, tasks, baselines))]
    if not rows:
        print("nothing scored", file=sys.stderr)
        return 1

    trap_cols: list[str] = []
    for row in rows:
        for k in row:
            if k not in ("run", "task", "cond", "_details") and k not in trap_cols:
                trap_cols.append(k)

    header = ["run", "cond"] + trap_cols
    widths = [max(len(h), 22) if h == "run" else max(len(h), 8) for h in header]
    print("  ".join(h.ljust(w) for h, w in zip(header, widths)))
    print("-" * (sum(widths) + 2 * len(widths)))
    for row in rows:
        cells = [row["run"], row["cond"]] + [row.get(c, "·") for c in trap_cols]
        print("  ".join(str(c).ljust(w) for c, w in zip(cells, widths)))
        if args.details:
            for tid, det in row["_details"].items():
                print(f"    {tid}: {det}")

    # Per-condition tallies for each trap column (fail / pass / inactive)
    print()
    for col in trap_cols:
        parts = []
        for cond in ("A", "B"):
            sub = [r for r in rows if r["cond"] == cond and col in r]
            if not sub:
                continue
            f = sum(1 for r in sub if r[col] == "fail")
            p = sum(1 for r in sub if r[col] == "pass")
            i = sum(1 for r in sub if r[col] == "inactive")
            parts.append(f"{cond}: fail {f} / pass {p} / inactive {i} (n={len(sub)})")
        print(f"{col:32} " + " | ".join(parts))

    if args.csv:
        with open(args.csv, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["run", "task", "cond"] + trap_cols)
            w.writeheader()
            for row in rows:
                w.writerow({k: row.get(k, "") for k in
                            ["run", "task", "cond"] + trap_cols})
        print(f"\nwrote {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
