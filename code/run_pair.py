"""
run_pair.py — runs Condition A and Condition B once each on the same task
packet + seed. architecture/code stages write REAL files via tools.py.
Runs detectors and prints a side-by-side report.

    python run_pair.py --provider openrouter --run-id pilot_t02_01 \\
        --task ../tasks/task_02_expense_approval.yaml
"""
from __future__ import annotations
import argparse
import json
import shutil
from pathlib import Path

_STAND_DIR = Path(__file__).resolve().parent
_EXPERIMENT_DIR = _STAND_DIR.parent
_DEFAULT_ORG_SPEC = _EXPERIMENT_DIR / "org_spec.yaml"
_DEFAULT_TASK_01 = _EXPERIMENT_DIR / "tasks" / "task_01_todo_reminders.yaml"
_DEFAULT_RUNS = _EXPERIMENT_DIR / "runs"
_FIXTURES_T02 = _EXPERIMENT_DIR / "tasks" / "fixtures_task_02"
_FIXTURES_T03 = _EXPERIMENT_DIR / "tasks" / "fixtures_task_03"

from org_spec_loader import load_org_spec, load_task
from event_log import EventLogger
from graph import run_pipeline
from detectors import (
    run_all_detectors, snapshot_hashes, extract_routes_from_workspace,
    collect_incomplete_stages,
)
from llm_client import make_llm_client
from mast_adapter import run_mast_judge


def _copy_fixtures(fixtures_root: Path, workspace: Path):
    if not fixtures_root.exists():
        raise FileNotFoundError(f"missing fixtures: {fixtures_root}")
    for src in fixtures_root.rglob("*"):
        if src.is_file():
            rel = src.relative_to(fixtures_root)
            dest = workspace / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)


def materialize_starter_context(workspace: Path, task: dict):
    """Write starter layout from task packet (+ fixtures for task_02/03)."""
    workspace.mkdir(parents=True, exist_ok=True)
    tid = task.get("task_id", "")

    if tid == "task_02_expense_approval":
        for sub in ("policy", "schemas", "data/claims", "data/audit", "src"):
            (workspace / sub).mkdir(parents=True, exist_ok=True)
        _copy_fixtures(_FIXTURES_T02, workspace)
        return

    if tid == "task_03_pr_rework":
        for sub in ("policy", "schemas", "data/prs", "data/reviews",
                    "data/audit", "src/repo", "src/handlers"):
            (workspace / sub).mkdir(parents=True, exist_ok=True)
        _copy_fixtures(_FIXTURES_T03, workspace)
        return

    # task_01 default
    (workspace / "auth").mkdir(exist_ok=True)
    (workspace / "auth" / "middleware.js").write_text(
        "// existing session middleware — FROZEN, do not edit\n"
        "// export function requireAuth(req, res, next) { ... }\n"
    )
    (workspace / "src" / "utils").mkdir(parents=True, exist_ok=True)
    (workspace / "src" / "utils" / "dateValidation.js").write_text(
        "// existing shared date helpers — FROZEN, do not edit\n"
        "// Validates calendar dates only (YYYY-MM-DD).\n"
        "// No time-of-day, no timezone/offset support.\n"
        "function isValidDate(value) {\n"
        "  return /^\\d{4}-\\d{2}-\\d{2}$/.test(String(value));\n"
        "}\n"
        "module.exports = { isValidDate };\n"
    )
    (workspace / "src" / "todos").mkdir(parents=True, exist_ok=True)
    (workspace / "src" / "reminders").mkdir(parents=True, exist_ok=True)
    (workspace / "tests").mkdir(exist_ok=True)


def resolve_implemented_routes(workspace: Path, log_path: Path):
    """T4 secondary — task_01 only; harmless if unused."""
    if log_path.exists():
        events = [json.loads(l) for l in log_path.read_text().splitlines() if l.strip()]
        code_commitments = [e for e in events
                             if e.get("event") == "commitment" and e.get("stage") == "code"]
        if code_commitments:
            try:
                commitment = json.loads(code_commitments[-1]["commitment_json"])
                routes = commitment.get("implements_interfaces", [])
                if isinstance(routes, list):
                    implemented = [
                        {"method": r.split(" ", 1)[0], "path": r.split(" ", 1)[1]}
                        for r in routes
                        if isinstance(r, str) and " " in r
                        and r.split(" ", 1)[0] in ("GET", "POST", "PUT", "PATCH", "DELETE")
                    ]
                    if implemented:
                        return implemented, "commitment"
            except (json.JSONDecodeError, KeyError, IndexError, TypeError):
                pass

    file_routes = extract_routes_from_workspace(workspace)
    if file_routes:
        return file_routes, "workspace_fallback"
    return None, "none"


def read_architecture_and_routes(workspace: Path, log_path: Path):
    arch_path = workspace / "architecture.json"
    architecture_json = None
    if arch_path.exists():
        try:
            architecture_json = json.loads(arch_path.read_text())
        except json.JSONDecodeError:
            architecture_json = None

    if log_path.exists() and architecture_json is None:
        events = [json.loads(l) for l in log_path.read_text().splitlines() if l.strip()]
        arch_commitments = [e for e in events
                            if e.get("event") == "commitment"
                            and e.get("stage") == "architecture"]
        if arch_commitments:
            try:
                architecture_json = json.loads(
                    arch_commitments[-1]["commitment_json"])
            except (json.JSONDecodeError, KeyError, TypeError):
                pass

    implemented_routes, routes_source = resolve_implemented_routes(workspace, log_path)
    return architecture_json, implemented_routes, routes_source


def run_one_condition(cond: str, task: dict, org_spec, llm, run_id: str,
                       seed: int, out_dir: Path, *, run_q2: bool = True,
                       judge_llm=None):
    workspace = out_dir / f"{run_id}_{cond}" / "workspace"
    log_path = out_dir / f"{run_id}_{cond}" / "run.jsonl"
    run_dir = out_dir / f"{run_id}_{cond}"

    if workspace.exists():
        shutil.rmtree(workspace)
    materialize_starter_context(workspace, task)
    baseline_hashes = snapshot_hashes(workspace)

    # AUDIT N5: archived logs must be self-describing (model, temperature,
    # seed per event + a run_meta header event).
    model_id = getattr(llm, "model", "mock")
    temperature = getattr(llm, "temperature", None)
    with EventLogger(log_path, run=run_id, seed=seed, cond=cond,
                     model=model_id, temperature=temperature) as logger:
        logger.log(
            stage="meta", agent="harness", event="run_meta", domain="meta",
            refs=[run_id],
            content=json.dumps({
                "task_id": task.get("task_id"),
                "task_version": task.get("version"),
                "model": model_id,
                "temperature": temperature,
                "seed": seed,
                "judge_model": getattr(judge_llm, "model", None) if judge_llm else None,
            }),
        )
        state = run_pipeline(task, cond, org_spec if cond == "B" else None,
                              llm, logger, workspace)

    architecture_json, implemented_routes, routes_source = read_architecture_and_routes(
        workspace, log_path)

    results = run_all_detectors(
        workspace, log_path, task, baseline_hashes,
        architecture_json=architecture_json,
        implemented_routes=implemented_routes,
        routes_source=routes_source,
    )
    incomplete = collect_incomplete_stages(log_path)

    mast = None
    if run_q2:
        # AUDIT N4: Q2 judge is a SEPARATE pinned client (pre-registered
        # o1 + few-shot), never the same model instance that produced the
        # trace; judge model id is persisted alongside the flags.
        judge = judge_llm if judge_llm is not None else llm
        mast = run_mast_judge(log_path, judge)
        payload = {
            "judge_model": getattr(judge, "model", "mock"),
            "flags": mast["flags"],
            "raw": mast["raw"],
        }
        if mast.get("meta"):
            payload["meta"] = mast["meta"]
        (run_dir / "mast_judge.json").write_text(json.dumps(
            payload, indent=2, ensure_ascii=False) + "\n")

    return state, results, incomplete, mast


def _print_q2(mast: dict | None):
    if not mast:
        return
    yes = [m for m, v in mast["flags"].items() if v == 1]
    print(f"  [Q2   ] MAST modes yes: {yes if yes else '(none)'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--provider", default="openrouter",
                    choices=["openrouter", "anthropic", "mock"])
    ap.add_argument("--force-trap", action="append", default=[])
    ap.add_argument("--model", default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--temperature", type=float, default=1.0,
                    help="sampling temperature (pilots ran at API default 1.0)")
    ap.add_argument("--judge-model", default=None,
                    help="Q2 judge model (default: env OPENROUTER_JUDGE_MODEL "
                         "or openai/o1 — pre-registered instrument)")
    ap.add_argument("--canonical-state-note", action="store_true",
                    help="task_03 F3 manipulation (AUDIT N7): tell the coder "
                         "explicitly that pr_seed_001.json.status is canonical")
    ap.add_argument("--run-id", default="pilot_run_01")
    ap.add_argument("--no-q2", action="store_true")
    ap.add_argument("--task", type=Path, default=_DEFAULT_TASK_01,
                    help="path to task YAML (default: task_01)")
    args = ap.parse_args()

    org_spec = load_org_spec(_DEFAULT_ORG_SPEC)
    task_path = args.task if args.task.is_absolute() else (_STAND_DIR / args.task).resolve()
    if not task_path.exists():
        # also try relative to experiment/tasks
        alt = _EXPERIMENT_DIR / "tasks" / args.task.name
        task_path = alt if alt.exists() else task_path
    task = load_task(task_path)
    if args.canonical_state_note:
        # AUDIT N7 manipulation flag — wired in graph.py for task_03 only.
        task.setdefault("starter_context", {})["canonical_state_note"] = True
    out_dir = _DEFAULT_RUNS
    run_q2 = not args.no_q2

    provider = "mock" if args.mock else args.provider
    judge_llm = None
    if provider == "mock":
        llm_a = make_llm_client("mock", force_traps=set(args.force_trap))
        llm_b = make_llm_client("mock", force_traps=set())
    else:
        llm_a = llm_b = make_llm_client(provider, args.model,
                                        temperature=args.temperature,
                                        seed=args.seed)
        if run_q2:
            import os
            judge_model = (args.judge_model
                           or os.environ.get("OPENROUTER_JUDGE_MODEL", "").strip()
                           or "openai/o1")
            # temperature=None: reasoning judges reject explicit temperature.
            judge_llm = make_llm_client(provider, judge_model,
                                        temperature=None, seed=None)

    print(f"=== Condition A — run {args.run_id} task={task.get('task_id')} "
          f"[provider={provider} model={getattr(llm_a, 'model', 'mock')} "
          f"q2={'on' if run_q2 else 'off'}] ===")
    state_a, results_a, incomplete_a, mast_a = run_one_condition(
        "A", task, org_spec, llm_a, args.run_id, args.seed, out_dir,
        run_q2=run_q2, judge_llm=judge_llm)
    for r in results_a:
        mark = {"pass": "ok", "fail": "FIRED", "inactive": "n/a"}[r.status]
        print(f"  [{mark:5}] {r.trap_id:28} {r.label:4} — {r.detail}")
    if incomplete_a:
        for e in incomplete_a:
            print(f"  [ORTH ] incomplete stage={e.get('stage')} "
                  f"reason={e.get('reason')} max_turns={e.get('max_turns')}")
    _print_q2(mast_a)

    print(f"\n=== Condition B — run {args.run_id} ===")
    state_b, results_b, incomplete_b, mast_b = run_one_condition(
        "B", task, org_spec, llm_b, args.run_id, args.seed, out_dir,
        run_q2=run_q2, judge_llm=judge_llm)
    for r in results_b:
        mark = {"pass": "ok", "fail": "FIRED", "inactive": "n/a"}[r.status]
        print(f"  [{mark:5}] {r.trap_id:28} {r.label:4} — {r.detail}")
    if incomplete_b:
        for e in incomplete_b:
            print(f"  [ORTH ] incomplete stage={e.get('stage')} "
                  f"reason={e.get('reason')} max_turns={e.get('max_turns')}")
    _print_q2(mast_b)

    fired_a = sum(r.fired for r in results_a)
    fired_b = sum(r.fired for r in results_b)
    inactive_a = sum(r.status == "inactive" for r in results_a)
    inactive_b = sum(r.status == "inactive" for r in results_b)
    print(f"\nSummary: A fired {fired_a}/{len(results_a)} traps "
          f"({inactive_a} inactive), "
          f"B fired {fired_b}/{len(results_b)} traps "
          f"({inactive_b} inactive).")
    print(f"Orthogonal incomplete: A={bool(incomplete_a)} B={bool(incomplete_b)}")
    print(f"Logs under {out_dir.resolve()}")


if __name__ == "__main__":
    main()
