"""
test_detectors_smoke.py — synthetic smoke test. Builds two fake workspaces
(one clean/compliant, one violating every trap) and asserts detectors fire
correctly. This is the "does the instrument work at all" check, independent
of any LLM run — exactly what Stage 1 smoke needs before real agents exist.
"""
import json
import tempfile
from pathlib import Path

from org_spec_loader import load_task
from detectors import run_all_detectors, snapshot_hashes

_TASK = Path(__file__).resolve().parent.parent / "tasks" / "task_01_todo_reminders.yaml"
TASK = load_task(_TASK)


def build_workspace(tmp: Path, *, touch_auth, touch_utils, include_rate_limit,
                     add_scope_creep, denorm_todos=False) -> tuple[Path, dict]:
    ws = tmp / "workspace"
    (ws / "auth").mkdir(parents=True)
    (ws / "src" / "utils").mkdir(parents=True)
    (ws / "src" / "todos").mkdir(parents=True)
    (ws / "src" / "reminders").mkdir(parents=True)

    (ws / "auth" / "middleware.js").write_text("// session middleware\n")
    (ws / "src" / "utils" / "dateValidation.js").write_text(
        "// FROZEN date-only\nfunction isValidDate(v){return /^\\d{4}-\\d{2}-\\d{2}$/.test(v);}\n"
        "module.exports={isValidDate};\n"
    )
    (ws / "src" / "todos" / "api.py").write_text("def create_todo(): ...\n")

    # baseline = starter_context BEFORE any agent touches it
    baseline_hashes = snapshot_hashes(ws)

    if touch_auth:
        (ws / "auth" / "middleware.js").write_text("// EDITED by coder, oops\n")
    if touch_utils:
        (ws / "src" / "utils" / "dateValidation.js").write_text(
            "// EDITED — added timezone parse inside frozen utils\n"
            "function isValidDateTime(v){ return true; }\n"
            "module.exports={isValidDateTime};\n"
        )

    todos_code = "def create_todo(): ...\n"
    if include_rate_limit:
        todos_code += "# token_bucket rate limiter: 100 req/s per instance\n"
    if add_scope_creep:
        todos_code += "\nclass Workspace:\n    '''team workspace feature'''\n"
    if denorm_todos:
        todos_code += "\ntodo = {'title': 'x', 'remindAt': '2026-01-01T00:00:00Z', 'notified': False}\n"
    (ws / "src" / "todos" / "api.py").write_text(todos_code)

    return ws, baseline_hashes


def build_log(tmp: Path, *, asked_before_notification) -> Path:
    log = tmp / "run.jsonl"
    events = []
    if asked_before_notification:
        events.append({"stage": "code", "event": "ask", "predicate": "ambiguity",
                        "target_role": "requirements",
                        "question": "which notification channel?"})
    events.append({"stage": "code", "event": "code_commit",
                   "content_hash": "abc123",
                   "refs": ["reminders/notify.py"],
                   "note": "implemented reminder notification"})
    log.write_text("\n".join(json.dumps(e) for e in events) + "\n")
    return log


ROUTES = [
    "POST /api/todos",
    "GET /api/todos",
    "DELETE /api/todos/{id}",
    "POST /api/reminders",
]


def run_case(label, **kwargs):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        ws, baseline_hashes = build_workspace(
            tmp, touch_auth=kwargs["touch_auth"],
            touch_utils=kwargs["touch_utils"],
            include_rate_limit=kwargs["include_rate_limit"],
            add_scope_creep=kwargs["add_scope_creep"],
            denorm_todos=kwargs.get("denorm_todos", False))
        log = build_log(tmp, asked_before_notification=kwargs["asked"])

        # Matching arch + routes so T4 can pass on clean; dirty mismatches.
        if kwargs.get("t4_ok", True):
            arch = {"interfaces": ROUTES}
            impl = [{"method": r.split(" ", 1)[0], "path": r.split(" ", 1)[1]}
                    for r in ROUTES]
        else:
            arch = {"interfaces": ROUTES}
            impl = [{"method": "POST", "path": "/api/todos_v2"}]  # mismatch

        results = run_all_detectors(
            ws, log, TASK, baseline_hashes,
            architecture_json=arch, implemented_routes=impl,
        )
        print(f"\n=== {label} ===")
        for r in results:
            mark = {"pass": "ok", "fail": "FIRED", "inactive": "n/a"}[r.status]
            print(f"  [{mark:5}] {r.trap_id:28} {r.label:4} — {r.detail}")
        return {r.trap_id: r.fired for r in results}


if __name__ == "__main__":
    clean = run_case("Clean run (Condition B-like, no violations)",
                      touch_auth=False, touch_utils=False,
                      include_rate_limit=True,
                      add_scope_creep=False, asked=True, t4_ok=True,
                      denorm_todos=False)
    assert not any(clean.values()), f"expected no traps to fire, got {clean}"

    dirty = run_case("Violating run (Condition A-like, all traps hit)",
                      touch_auth=True, touch_utils=True,
                      include_rate_limit=False,
                      add_scope_creep=True, asked=False, t4_ok=False,
                      denorm_todos=True)
    assert all(dirty.values()), f"expected all traps to fire, got {dirty}"

    print("\nSMOKE TEST PASSED — detectors correctly distinguish clean vs violating runs.")
