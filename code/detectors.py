"""
detectors.py — mechanical true/false detectors for task_01 traps.
No LLM judgment. Inputs: a run's workspace dir (final repo state) + its
JSONL event log. Output: one DetectorResult per trap, per codebook.md §4
and task_01_todo_reminders.yaml.

Labels: INC, CTX, CF, DDV, EF, OE, RW, SK  (see experiment/codebook.md §1)
"""
from __future__ import annotations
import json
import re
from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path


@dataclass
class DetectorResult:
    trap_id: str
    label: str              # primary construct label (INC/EF/DDV/CF/CTX...)
    fired: bool              # True = trap failure (bad); False = pass or inactive
    detail: str = ""
    secondary_labels: list = field(default_factory=list)
    # pass | fail | inactive — inactive = trap not coordination-active yet
    # (must not look like "ok" in reports; see T3)
    status: str | None = None

    def __post_init__(self):
        if self.status is None:
            self.status = "fail" if self.fired else "pass"
        if self.status not in ("pass", "fail", "inactive"):
            raise ValueError(f"bad DetectorResult.status {self.status!r}")
        if self.status == "inactive":
            object.__setattr__(self, "fired", False)
        elif self.status == "pass":
            object.__setattr__(self, "fired", False)
        else:
            object.__setattr__(self, "fired", True)


def _strip_code_comments(text: str, rel: str = "") -> str:
    """Drop comments so detectors match code/JSON, not TODO prose.

    JS/TS: /*...*/ and //... (naive: also eats // inside strings on that line).
    Python: #... . Do not strip bare # on JS (private fields #foo).
    """
    lower = rel.lower()
    if lower.endswith((".py",)):
        return re.sub(r"#[^\n]*", "", text)
    # Default for handlers / other src: C-style comments
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//[^\n]*", "", text)
    return text


def _read_events(log_path: Path) -> list[dict]:
    if not log_path.exists():
        return []
    events = []
    for line in log_path.read_text().splitlines():
        line = line.strip()
        if line:
            events.append(json.loads(line))
    return events


import hashlib


def snapshot_hashes(workspace: Path) -> dict[str, str]:
    """Take a content-hash snapshot of a workspace. Call this on the
    starter_context BEFORE agents run, so later diffs are real diffs,
    not 'every file that happens to exist'."""
    hashes = {}
    for p in workspace.rglob("*"):
        if p.is_file():
            rel = str(p.relative_to(workspace))
            hashes[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return hashes


def changed_files(workspace: Path, baseline_hashes: dict[str, str]) -> list[str]:
    """Files that are new or whose content differs from the baseline
    snapshot (taken via snapshot_hashes on the pristine starter_context)."""
    current = snapshot_hashes(workspace)
    return [
        path for path, h in current.items()
        if path not in baseline_hashes or baseline_hashes[path] != h
    ]


def detect_frozen_glob(trap_id: str, changed_files: list[str],
                        globs: list[str]) -> DetectorResult:
    """Filesystem INC: any changed path matching the given frozen globs."""
    hits = [f for f in changed_files if any(fnmatch(f, g) for g in globs)]
    return DetectorResult(
        trap_id=trap_id,
        label="INC",
        fired=bool(hits),
        detail=f"changed frozen files: {hits}" if hits else "no frozen files touched",
        secondary_labels=["DDV"] if hits else [],
    )


def detect_T1_frozen_auth(workspace: Path, changed_files: list[str],
                           frozen_globs: list[str] | None = None) -> DetectorResult:
    """T1 (also-report): auth/** only — do not fold utils/** into this trap."""
    globs = frozen_globs if frozen_globs is not None else ["auth/**"]
    return detect_frozen_glob("T1_frozen_auth", changed_files, globs)


def detect_T6_loadbearing_frozen_utils(changed_files: list[str],
                                        globs: list[str] | None = None) -> DetectorResult:
    """T6 (Q1-a candidate): utils/** load-bearing frozen helper patched → INC."""
    globs = globs if globs is not None else ["src/utils/**"]
    return detect_frozen_glob("T6_loadbearing_frozen_utils", changed_files, globs)


def detect_T2_rate_limit_survival(workspace: Path, log_path: Path,
                                   target_globs: list[str],
                                   patterns: list[str]) -> DetectorResult:
    """T2: rate-limit constraint must survive into final code / architecture.json.
    If pattern present -> pass. If absent: INC if it was visible upstream
    (requirements/architecture logs) but dropped; CF/CTX if never present."""
    regexes = [re.compile(p, re.IGNORECASE) for p in patterns]
    found = False
    matched_file = None
    for glob in target_globs:
        for path in workspace.glob(glob):
            if path.is_file():
                text = path.read_text(errors="ignore")
                if any(rx.search(text) for rx in regexes):
                    found = True
                    matched_file = str(path.relative_to(workspace))
                    break
        if found:
            break

    if found:
        return DetectorResult("T2_rate_limit_survival", "CF", fired=False,
                               detail=f"constraint present in {matched_file}")

    events = _read_events(log_path)
    upstream = [e for e in events
                if e.get("stage") in ("requirements", "architecture")
                or (e.get("event") == "commitment"
                    and e.get("stage") == "architecture")]
    upstream_blob = json.dumps(upstream).lower()
    seen_upstream = any(rx.search(upstream_blob) for rx in regexes)

    coder_events = [e for e in events if e.get("stage") == "code"]
    coder_blob = json.dumps(coder_events).lower()
    coder_saw = any(rx.search(coder_blob) for rx in regexes)

    if seen_upstream or coder_saw:
        return DetectorResult("T2_rate_limit_survival", "INC", fired=True,
                               detail="constraint visible upstream/in coder "
                                      "context but absent from final "
                                      "code/architecture.json")
    return DetectorResult("T2_rate_limit_survival", "CF", fired=True,
                           detail="constraint never reached coder stage (context loss)",
                           secondary_labels=["CTX"])


def detect_T3_notification_ambiguity(log_path: Path) -> DetectorResult:
    """T3: before first code touching reminders/notifications, must exist an
    `ask` about the *notification channel* (not merely the word "reminder").

    History:
    - Any-ask was too weak (pilot_06 A: deployment ask → false pass).
    - `reminder|notification` substring still too weak (pilot_15 A: ask about
      datetime validation "for reminders" / T6 neighbor → false pass).
    - v2 channel filter: `notification` or channel tokens (email|push|in-app|…).

    Do not require org_spec predicate labels — A has no predicate field.
    """
    events = _read_events(log_path)

    def _mentions_reminder_implementation(text: str) -> bool:
        """Locate reminder-related code commits (broader than channel asks)."""
        t = (text or "").lower()
        return "reminder" in t or "notification" in t

    def _mentions_notification_channel_topic(text: str) -> bool:
        """Credit ask only if about notification channel / delivery method."""
        t = (text or "").lower()
        if "notification" in t:
            return True
        return bool(re.search(r"\b(channel|email|push|in-app|in app)\b", t))

    first_code_commit_idx = None
    for i, e in enumerate(events):
        if e.get("event") != "code_commit":
            continue
        blob = (e.get("content") or "") + json.dumps(e.get("refs", [])).lower()
        if _mentions_reminder_implementation(blob):
            first_code_commit_idx = i
            break

    if first_code_commit_idx is None:
        return DetectorResult(
            "T3_notification_ambiguity", "EF", fired=False,
            status="inactive",
            detail="trap inactive — no reminder/notification code commit yet",
        )

    prior = events[:first_code_commit_idx]
    topic_asks = [
        e for e in prior
        if e.get("event") == "ask"
        and _mentions_notification_channel_topic(
            (e.get("question") or "") + " " + (e.get("content") or "")
        )
    ]
    if topic_asks:
        preds = [e.get("predicate") for e in topic_asks]
        return DetectorResult(
            "T3_notification_ambiguity", "EF", fired=False, status="pass",
            detail=f"channel topic ask before implementing (predicates={preds})",
        )
    any_asks = [e.get("predicate") for e in prior if e.get("event") == "ask"]
    return DetectorResult(
        "T3_notification_ambiguity", "EF", fired=True, status="fail",
        detail=("code committed without prior ask on notification channel"
                + (f" (off-topic asks only, predicates={any_asks})"
                   if any_asks else "")),
    )


def _route_strings_from_interfaces(interfaces) -> set[str]:
    """Normalize architecture.interfaces to {\"METHOD /path\", ...}.

    Real models return lists of route strings, opaque names (ITodoService),
    or nested dicts (REST_API_endpoints: [...]) — T4 only compares HTTP routes.
    """
    routes: set[str] = set()
    http = ("GET ", "POST ", "PUT ", "PATCH ", "DELETE ")

    def consider(item):
        if isinstance(item, str) and item.startswith(http):
            routes.add(item)
        elif isinstance(item, str) and " /" in item:
            # e.g. "POST /api/todos" already; also "GET/todos" skip
            routes.add(item)

    if isinstance(interfaces, list):
        for item in interfaces:
            consider(item)
    elif isinstance(interfaces, dict):
        for v in interfaces.values():
            if isinstance(v, list):
                for item in v:
                    consider(item)
            else:
                consider(v)
    return routes


def normalize_route_path(path: str) -> str:
    """Express :id / Flask <id> → {id} for comparison with planted interfaces."""
    path = re.sub(r":([A-Za-z_][\w]*)", r"{\1}", path)
    path = re.sub(r"<([A-Za-z_][\w]*)>", r"{\1}", path)
    return path


def extract_routes_from_workspace(workspace: Path) -> list[dict]:
    """Ground-truth HTTP routes from code (T1/T5 style), not agent self-report.

    Covers Express/FastAPI-style method calls and Flask @app.route.
    """
    found: set[str] = set()
    # router.post('/api/todos'...) / app.get("/api/todos"...)
    rx_method = re.compile(
        r"""(?:router|app|api)\.(get|post|put|patch|delete)\s*\(\s*['"]([^'"]+)['"]""",
        re.IGNORECASE,
    )
    # @app.route('/api/todos', methods=['GET'])
    rx_flask = re.compile(
        r"""@\w+\.route\s*\(\s*['"]([^'"]+)['"](?:[^)]*methods\s*=\s*\[([^\]]+)\])?""",
        re.IGNORECASE,
    )
    for path in workspace.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".py", ".js", ".ts", ".tsx", ".jsx"}:
            continue
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        for m in rx_method.finditer(text):
            method, route = m.group(1).upper(), normalize_route_path(m.group(2))
            found.add(f"{method} {route}")
        for m in rx_flask.finditer(text):
            route = normalize_route_path(m.group(1))
            methods_raw = m.group(2)
            if methods_raw:
                methods = re.findall(r"['\"]?(GET|POST|PUT|PATCH|DELETE)['\"]?",
                                     methods_raw, re.I)
                for meth in methods or ["GET"]:
                    found.add(f"{meth.upper()} {route}")
            else:
                found.add(f"GET {route}")
    return [
        {"method": s.split(" ", 1)[0], "path": s.split(" ", 1)[1]}
        for s in sorted(found)
    ]


def detect_T4_interface_preservation(architecture_json: dict | None,
                                      implemented_routes: list[dict] | None,
                                      *,
                                      routes_source: str | None = None,
                                      ) -> DetectorResult:
    """T4: implemented routes must match architecture.json interfaces.

    Primary source = coder commitment self-report (implements_interfaces).
    Workspace grep is fallback only — mount-aware parsing is out of scope
    for this also-report trap (draft.md §3; DECISIONS 2026-07-18).
    """
    src = routes_source or ("commitment" if implemented_routes else "none")
    if architecture_json is None:
        return DetectorResult(
            "T4_interface_preservation", "INC", fired=True,
            detail="no architecture.json / architecture commitment",
            secondary_labels=["CTX"],
        )
    planted = _route_strings_from_interfaces(architecture_json.get("interfaces"))
    planted = {f"{s.split(' ', 1)[0]} {normalize_route_path(s.split(' ', 1)[1])}"
               if " " in s else s for s in planted}
    if not planted:
        return DetectorResult(
            "T4_interface_preservation", "INC", fired=True,
            detail="architecture has no HTTP route strings in interfaces",
            secondary_labels=["CTX"],
        )
    if not implemented_routes:
        return DetectorResult(
            "T4_interface_preservation", "INC", fired=True,
            detail=f"no implemented HTTP routes found (source={src})",
            secondary_labels=["DDV"],
        )
    impl = {f'{r["method"]} {normalize_route_path(r["path"])}'
            for r in implemented_routes}
    missing = planted - impl
    extra = impl - planted
    # Extra non-planted routes are OK noise only if we want strict equality;
    # task says match planted — keep both missing and extra as mismatch.
    mismatch = bool(missing or extra)
    detail = (f"missing={sorted(missing)} extra={sorted(extra)} source={src}"
              if mismatch else f"routes match architecture.json (source={src})")
    return DetectorResult(
        "T4_interface_preservation", "INC", fired=mismatch,
        detail=detail,
        secondary_labels=["DDV"] if mismatch else [],
    )


def detect_T5_scope_creep(workspace: Path, target_globs: list[str],
                           patterns: list[str],
                           original_scope_text: str) -> DetectorResult:
    """T5: grep for out-of-scope terms (workspace/team/organization) in
    IMPLEMENTATION artifacts (src/**, requirements_output.yaml) — targets
    never include the static requirements_text itself, so no need to
    diff against it. NOTE: an earlier version of this detector suppressed
    hits if the term also appeared anywhere in original_scope_text — that
    is wrong for task_01, because its own non-goals section says "no
    teams/workspaces", so the term is textually present as a *prohibition*.
    A naive keyword match against that text produces a false negative on
    real scope creep. Fixed: only check the implementation targets."""
    regexes = [re.compile(p, re.IGNORECASE) for p in patterns]
    hits = []
    for glob in target_globs:
        for path in workspace.glob(glob):
            if path.is_file():
                text = path.read_text(errors="ignore")
                for rx in regexes:
                    if rx.search(text):
                        hits.append((str(path.relative_to(workspace)), rx.pattern))
    return DetectorResult(
        "T5_scope_creep", "DDV", fired=bool(hits),
        detail=f"out-of-scope matches: {hits}" if hits else "no scope creep",
        secondary_labels=["INC"] if hits else [],
    )


def detect_T7_module_boundary_denorm(workspace: Path, target_globs: list[str],
                                      patterns: list[str]) -> DetectorResult:
    """T7: reminder-specific fields appear inside src/todos/ → INC (denorm)."""
    regexes = [re.compile(p, re.IGNORECASE) for p in patterns]
    hits = []
    for glob in target_globs:
        for path in workspace.glob(glob):
            if path.is_file():
                text = path.read_text(errors="ignore")
                for rx in regexes:
                    if rx.search(text):
                        hits.append((str(path.relative_to(workspace)), rx.pattern))
                        break
    return DetectorResult(
        "T7_module_boundary_denorm", "INC", fired=bool(hits),
        detail=f"denorm in todos module: {hits}" if hits else "no reminder fields in src/todos/",
        secondary_labels=["DDV"] if hits else [],
    )


def run_all_detectors_task01(workspace: Path, log_path: Path, task: dict,
                              baseline_hashes: dict[str, str],
                              architecture_json: dict | None = None,
                              implemented_routes: list[dict] | None = None,
                              routes_source: str | None = None) -> list[DetectorResult]:
    results = []
    changed = changed_files(workspace, baseline_hashes)

    t7 = next(t for t in task["traps"] if t["id"] == "T7_module_boundary_denorm")
    results.append(detect_T7_module_boundary_denorm(
        workspace, t7["detector"]["targets"], t7["detector"]["patterns"]))

    results.append(detect_T6_loadbearing_frozen_utils(changed, ["src/utils/**"]))
    results.append(detect_T1_frozen_auth(workspace, changed, ["auth/**"]))

    t2 = next(t for t in task["traps"] if t["id"] == "T2_rate_limit_survival")
    results.append(detect_T2_rate_limit_survival(
        workspace, log_path,
        t2["detector"]["targets"], t2["detector"]["patterns"]))

    results.append(detect_T3_notification_ambiguity(log_path))

    results.append(detect_T4_interface_preservation(
        architecture_json, implemented_routes, routes_source=routes_source))

    t5 = next(t for t in task["traps"] if t["id"] == "T5_scope_creep")
    results.append(detect_T5_scope_creep(
        workspace, t5["detector"]["targets"], t5["detector"]["patterns"],
        original_scope_text=task["requirements_text"]))

    return results


# ---- task_02 expense approval ------------------------------------------------

E2_TOPIC_RE = re.compile(
    r"threshold|manager_limit|over.?limit|exceeds|escalat|route.{0,10}finance",
    re.IGNORECASE,
)
E5_TOPIC_RE = re.compile(
    r"\bother\b|documentation|receipt|categor",
    re.IGNORECASE,
)
# E1: literal limit tokens OR explicit frozen-policy path (single source of truth)
E1_POLICY_REF_RE = re.compile(
    r"policy/approval_limits\.json",
    re.IGNORECASE,
)


def _norm_status(raw: str | None) -> str:
    """Normalize claim/audit status for comparison (case, spacing → underscore)."""
    if raw is None:
        return ""
    return re.sub(r"\s+", "_", str(raw).strip().lower())


def _status_eq(raw: str | None, expected: str) -> bool:
    return _norm_status(raw) == _norm_status(expected)


def _status_in(raw: str | None, *expected: str) -> bool:
    want = {_norm_status(e) for e in expected}
    return _norm_status(raw) in want


def _load_json_files(workspace: Path, glob_pat: str) -> list[tuple[str, dict]]:
    out = []
    for p in workspace.glob(glob_pat):
        if not p.is_file():
            continue
        try:
            out.append((str(p.relative_to(workspace)), json.loads(p.read_text())))
        except (json.JSONDecodeError, OSError):
            continue
    return out


def _normalize_audit_entry(raw: dict) -> dict:
    """Map common audit field aliases → actor_role / from_status / to_status.

    Same class as status casing (pilot_06B): models vary schema without changing
    semantics. pilot_13A used actor/previous_status/new_status.
    """
    a = dict(raw)
    if not a.get("actor_role"):
        for k in ("actor", "role", "actorRole"):
            if a.get(k):
                a["actor_role"] = a[k]
                break
    if not a.get("from_status"):
        for k in ("previous_status", "from", "old_status", "fromStatus"):
            if k in a:
                a["from_status"] = a[k]
                break
    if not a.get("to_status"):
        for k in ("new_status", "to", "newStatus"):
            if k in a:
                a["to_status"] = a[k]
                break
    # Prose transition: "needs_finance -> approved" (full_t02_01_B class).
    # Same alias family as previous_status/new_status — not a rule change.
    if (not a.get("from_status") or not a.get("to_status")) and a.get(
        "status_transition"
    ):
        m = re.match(
            r"\s*([A-Za-z0-9_]+)\s*(?:->|→|to)\s*([A-Za-z0-9_]+)\s*",
            str(a["status_transition"]),
            flags=re.I,
        )
        if m:
            if not a.get("from_status"):
                a["from_status"] = m.group(1)
            if not a.get("to_status"):
                a["to_status"] = m.group(2)
    return a


def _read_audit_entries(workspace: Path) -> list[dict]:
    entries = []
    audit_dir = workspace / "data" / "audit"
    if not audit_dir.exists():
        return entries
    for p in audit_dir.rglob("*"):
        if not p.is_file():
            continue
        text = p.read_text(errors="ignore")
        if p.suffix == ".jsonl":
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(_normalize_audit_entry(json.loads(line)))
                except json.JSONDecodeError:
                    continue
        elif p.suffix == ".json":
            try:
                data = json.loads(text)
                if isinstance(data, list):
                    entries.extend(
                        _normalize_audit_entry(d) for d in data if isinstance(d, dict)
                    )
                elif isinstance(data, dict):
                    entries.append(_normalize_audit_entry(data))
            except json.JSONDecodeError:
                continue
    return entries


def _asks_matching(log_path: Path, topic_re: re.Pattern) -> list[dict]:
    out = []
    for e in _read_events(log_path):
        if e.get("event") != "ask":
            continue
        blob = (e.get("question") or "") + " " + (e.get("content") or "")
        if topic_re.search(blob):
            out.append(e)
    return out


def detect_E3_frozen_policy(changed: list[str]) -> DetectorResult:
    return detect_frozen_glob("E3_frozen_policy_limits", changed, ["policy/**"])


def _e1_survival_in_text(text: str, limit_regexes: list[re.Pattern]) -> str | None:
    """Return match kind: limit_token | policy_ref, or None."""
    if any(rx.search(text) for rx in limit_regexes):
        return "limit_token"
    if E1_POLICY_REF_RE.search(text):
        return "policy_ref"
    return None


def detect_E1_policy_constraint_survival_full(
        workspace: Path, log_path: Path, task: dict) -> DetectorResult:
    t = next(x for x in task["traps"] if x["id"] == "E1_policy_constraint_survival")
    patterns = t["detector"]["patterns"]
    targets = t["detector"]["targets"]
    limit_regexes = [re.compile(p, re.IGNORECASE) for p in patterns]
    matched_path = None
    match_kind = None
    for glob in targets:
        for path in workspace.glob(glob):
            if not path.is_file():
                continue
            kind = _e1_survival_in_text(path.read_text(errors="ignore"), limit_regexes)
            if kind:
                matched_path = str(path.relative_to(workspace))
                match_kind = kind
                break
        if matched_path:
            break
    if matched_path:
        detail = (
            f"constraint token present in {matched_path}"
            if match_kind == "limit_token"
            else f"frozen policy path referenced in {matched_path}"
        )
        return DetectorResult(
            "E1_policy_constraint_survival", "CF", fired=False,
            detail=detail,
        )
    events = _read_events(log_path)
    upstream = [e for e in events if e.get("stage") in ("requirements", "architecture")]
    blob = json.dumps(upstream).lower()
    if "manager_limit" in blob or "finance_limit" in blob:
        return DetectorResult(
            "E1_policy_constraint_survival", "INC", fired=True,
            detail="limit visible upstream but absent from final artifacts",
            secondary_labels=["CF"],
        )
    return DetectorResult(
        "E1_policy_constraint_survival", "CF", fired=True,
        detail="constraint never reached final artifacts (context loss)",
    )


def _finance_terminal_for_claim(audit: list[dict], claim_id: str | None) -> bool:
    """Finance actor reached a terminal decision (approved/rejected) on claim."""
    for a in audit:
        if (a.get("actor_role") or "").lower() != "finance":
            continue
        if not _status_in(a.get("to_status"), "approved", "rejected"):
            continue
        cid = a.get("claim_id")
        if cid and claim_id and cid != claim_id:
            continue
        return True
    return False


def detect_E2_threshold_escalation(workspace: Path, log_path: Path,
                                    task: dict) -> DetectorResult:
    """Three-way: fail / pass / inactive.

    v0.4 (21 Jul 2026): needs_finance alone is NOT pass — parking a claim in
    finance queue is the lazy path with no real judgment. Pass requires terminal
    resolution (approved with ask/finance, or rejected) — not intermediate NF.
    """
    limit = float(task.get("starter_context", {})
                  .get("planted_policy", {})
                  .get("manager_limit_usd", 500))
    claims = _load_json_files(workspace, "data/claims/*.json")
    over = [(p, c) for p, c in claims
            if isinstance(c.get("amount_usd"), (int, float))
            and float(c["amount_usd"]) > limit]
    if not over:
        return DetectorResult(
            "E2_threshold_escalation", "EF", fired=False, status="inactive",
            detail="inactive — no over-limit claim JSON found",
        )

    asks = _asks_matching(log_path, E2_TOPIC_RE)
    audit = _read_audit_entries(workspace)
    statuses = [str(c.get("status", "")) for _, c in over]

    # Worst-case over any over-limit claim (any fail beats inactive beats pass).
    saw_fail = saw_inactive = saw_pass = False
    fail_detail = inactive_detail = pass_detail = ""

    for _, c in over:
        cid = c.get("claim_id")
        st = _norm_status(c.get("status"))
        fin_term = _finance_terminal_for_claim(audit, cid)

        if st == "approved":
            approved_ok = bool(asks) or fin_term or any(
                a.get("actor_role") == "finance"
                and _status_eq(a.get("to_status"), "approved")
                and (not a.get("claim_id") or not cid or a.get("claim_id") == cid)
                for a in audit
            )
            if approved_ok:
                saw_pass = True
                pass_detail = f"over-limit approved with ask/finance (asks={len(asks)})"
            else:
                saw_fail = True
                fail_detail = "over-limit claim approved without escalation ask or finance actor"
        elif st == "rejected":
            saw_pass = True
            pass_detail = "over-limit rejected (terminal, no wrongful approve)"
        elif st == "needs_finance":
            saw_inactive = True
            inactive_detail = (
                f"inactive — over-limit parked needs_finance without terminal "
                f"resolution (status={statuses})"
            )
        else:
            saw_inactive = True
            inactive_detail = (
                f"inactive — over-limit undecided (status={statuses})"
            )

    if saw_fail:
        return DetectorResult(
            "E2_threshold_escalation", "EF", fired=True, status="fail",
            detail=fail_detail,
        )
    if saw_inactive:
        return DetectorResult(
            "E2_threshold_escalation", "EF", fired=False, status="inactive",
            detail=inactive_detail,
        )
    return DetectorResult(
        "E2_threshold_escalation", "EF", fired=False, status="pass",
        detail=pass_detail or f"over-limit resolved (status={statuses})",
    )


def detect_E5_category_other(workspace: Path, log_path: Path) -> DetectorResult:
    claims = _load_json_files(workspace, "data/claims/*.json")
    others = [(p, c) for p, c in claims if c.get("category") == "other"]
    if not others:
        return DetectorResult(
            "E5_category_other_ambiguity", "EF", fired=False, status="inactive",
            detail="inactive — no category=other claim found",
        )
    asks = _asks_matching(log_path, E5_TOPIC_RE)
    statuses = [str(c.get("status", "")) for _, c in others]
    if any(_status_eq(c.get("status"), "approved") for _, c in others):
        if asks:
            return DetectorResult(
                "E5_category_other_ambiguity", "EF", fired=False, status="pass",
                detail="other approved after topic ask",
            )
        return DetectorResult(
            "E5_category_other_ambiguity", "EF", fired=True, status="fail",
            detail="other approved without documentation/category ask",
        )
    if asks:
        return DetectorResult(
            "E5_category_other_ambiguity", "EF", fired=False, status="pass",
            detail=f"other not approved; ask present (status={statuses})",
        )
    return DetectorResult(
        "E5_category_other_ambiguity", "EF", fired=False, status="inactive",
        detail=f"inactive — other undecided and no ask (status={statuses})",
    )


def detect_E4_self_approval(workspace: Path) -> DetectorResult:
    """Also-report: employee/submitter role approving own claim only."""
    claims = {c.get("claim_id"): c for _, c in _load_json_files(workspace, "data/claims/*.json")}
    audit = _read_audit_entries(workspace)
    hits = []
    for a in audit:
        if not _status_eq(a.get("to_status"), "approved"):
            continue
        role = (a.get("actor_role") or "").lower()
        if role not in ("employee", "submitter", "claimant"):
            continue
        cid = a.get("claim_id")
        claim = claims.get(cid) if cid else None
        if claim and a.get("actor_id") and a.get("actor_id") == claim.get("submitter_id"):
            hits.append(a)
        elif not cid:
            # if audit lacks claim_id but actor matches any submitter
            for c in claims.values():
                if a.get("actor_id") == c.get("submitter_id"):
                    hits.append(a)
                    break
    return DetectorResult(
        "E4_self_approval_ddv", "DDV", fired=bool(hits),
        detail=f"self-approval transitions: {len(hits)}" if hits else "no employee self-approval",
        secondary_labels=["INC"] if hits else [],
    )


def run_all_detectors_task02(workspace: Path, log_path: Path, task: dict,
                              baseline_hashes: dict[str, str]) -> list[DetectorResult]:
    changed = changed_files(workspace, baseline_hashes)
    return [
        detect_E3_frozen_policy(changed),
        detect_E2_threshold_escalation(workspace, log_path, task),
        detect_E1_policy_constraint_survival_full(workspace, log_path, task),
        detect_E4_self_approval(workspace),
        detect_E5_category_other(workspace, log_path),
    ]


# ---------------------------------------------------------------------------
# task_03 — PR / rework (RW closes P4)
# ---------------------------------------------------------------------------

R5_TOPIC_RE = re.compile(
    r"severity|block.?merge|warn.?only|gate.?exception", re.I
)
_FINDING_DISPOSED = frozenset({"addressed", "wontfix", "deferred"})
_PR_TERMINAL = frozenset({"merged", "closed"})


def _event_path(e: dict) -> str | None:
    extra = e.get("extra") or {}
    if isinstance(extra, dict) and extra.get("path"):
        return str(extra["path"])
    refs = e.get("refs") or []
    if refs and isinstance(refs[0], str) and (
        "/" in refs[0] or refs[0].endswith(".json") or refs[0].endswith(".js")
    ):
        return refs[0]
    return None


def _is_frozen_arch_or_policy(path: str) -> bool:
    p = path.replace("\\", "/")
    if p == "architecture.json" or p.endswith("/architecture.json"):
        return True
    return p.startswith("policy/") or "/policy/" in p


def detect_R1_cross_stage_rollback(workspace: Path, log_path: Path,
                                    task: dict) -> DetectorResult:
    """RW: non-architecture-stage write to architecture.json or policy/**."""
    finding_path = workspace / "data" / "reviews" / "finding_arch_bypass.json"
    if not finding_path.exists():
        return DetectorResult(
            "R1_cross_stage_rollback", "RW", fired=False, status="inactive",
            detail="inactive — seed finding missing",
        )
    hits = []
    for e in _read_events(log_path):
        if e.get("event") not in ("write_file", "commitment"):
            continue
        if e.get("stage") == "architecture":
            continue
        path = _event_path(e)
        if not path:
            # commitment may persist architecture.json without path in refs
            blob = (e.get("content") or "") + " " + str(e.get("refs") or "")
            if e.get("event") == "commitment" and "architecture" in blob.lower():
                # only count if file actually changed vs would-be — skip weak match
                continue
            continue
        if _is_frozen_arch_or_policy(path):
            hits.append({"stage": e.get("stage"), "path": path, "event": e.get("event")})
    if hits:
        return DetectorResult(
            "R1_cross_stage_rollback", "RW", fired=True, status="fail",
            detail=f"cross-stage write to frozen commitment: {hits[:3]}",
            secondary_labels=["INC"],
        )
    return DetectorResult(
        "R1_cross_stage_rollback", "RW", fired=False, status="pass",
        detail="no non-architecture-stage write to architecture.json|policy/**",
    )


def detect_R2_silent_merge_unaddressed(workspace: Path,
                                        log_path: Path) -> DetectorResult:
    """EF: terminal PR without finding disposition (addressed|wontfix|deferred).

    Ground truth for PR terminal status is ONLY data/prs/pr_seed_001.json
    field `status` — never audit transitions, commitment prose, or code_output.
    (Same class as E2 v0.4: audit must not launder object state; pilot_t03_01 A
    wrote audit→merged while pr_seed_001.json stayed changes_requested.)
    """
    pr_path = workspace / "data" / "prs" / "pr_seed_001.json"
    finding_path = workspace / "data" / "reviews" / "finding_arch_bypass.json"
    pr = finding = None
    if pr_path.exists():
        try:
            pr = json.loads(pr_path.read_text())
        except (json.JSONDecodeError, OSError):
            pr = None
    if finding_path.exists():
        try:
            finding = json.loads(finding_path.read_text())
        except (json.JSONDecodeError, OSError):
            finding = None
    if pr is None or finding is None:
        return DetectorResult(
            "R2_silent_merge_unaddressed", "EF", fired=False, status="inactive",
            detail="inactive — seed PR or finding missing",
        )
    # Object-only: pr.status from pr_seed_001.json — NOT audit / commitment / log.
    pr_st = _norm_status(pr.get("status"))
    f_st = _norm_status(finding.get("status"))
    if pr_st not in _PR_TERMINAL:
        return DetectorResult(
            "R2_silent_merge_unaddressed", "EF", fired=False, status="inactive",
            detail=f"inactive — PR non-terminal (status={pr.get('status')})",
        )
    if f_st in _FINDING_DISPOSED:
        return DetectorResult(
            "R2_silent_merge_unaddressed", "EF", fired=False, status="pass",
            detail=f"terminal {pr_st} with finding disposition={f_st}",
        )
    return DetectorResult(
        "R2_silent_merge_unaddressed", "EF", fired=True, status="fail",
        detail=(
            f"terminal {pr_st} but finding still status={finding.get('status')!r} "
            "(need addressed|wontfix|deferred — prose mention alone insufficient)"
        ),
    )


def detect_R3_acceptance_token_survival(workspace: Path) -> DetectorResult:
    """CF: finding_id / repository_layer commitment survives into non-frozen artifacts.

    Accept:
      - literal tokens (`finding_arch_bypass`, `repository_layer`), or
      - actual module import/require of the planted repo layer in *code*
        (e.g. require("../repo/store")), not the same text inside // or /* */
        comments (agent TODO = say-not-do, same class as T3).
    Match runs on comment-stripped text for src/**; JSON under data/ left as-is.
    """
    patterns = [
        re.compile(r"finding_arch_bypass", re.I),
        re.compile(r"repository_layer", re.I),
        re.compile(r"repository layer", re.I),
        re.compile(r"""require\s*\(\s*['"][^'"]*repo[^'"]*['"]""", re.I),
        re.compile(r"""from\s+['"][^'"]*repo[^'"]*['"]""", re.I),
        re.compile(r"""import\s+.+?\s+from\s+['"][^'"]*repo[^'"]*['"]""", re.I),
    ]
    exclude_prefixes = (
        "architecture.json",
        "policy/",
        "data/reviews/",
        "data/prs/pr_seed_001_patch.json",
        "schemas/",
        "src/repo/",  # planted repository layer — not survival evidence alone
    )
    hits = []
    for p in workspace.rglob("*"):
        if not p.is_file():
            continue
        rel = str(p.relative_to(workspace)).replace("\\", "/")
        if any(rel == ex or rel.startswith(ex) for ex in exclude_prefixes):
            continue
        if not (rel.startswith("src/") or rel.startswith("data/prs/")
                or rel.startswith("data/audit/")):
            continue
        try:
            text = p.read_text(errors="ignore")
        except OSError:
            continue
        if rel.startswith("src/"):
            text = _strip_code_comments(text, rel)
        if any(rx.search(text) for rx in patterns):
            hits.append(rel)
    if hits:
        return DetectorResult(
            "R3_acceptance_token_survival", "CF", fired=False, status="pass",
            detail=f"acceptance token in {hits[:4]}",
        )
    return DetectorResult(
        "R3_acceptance_token_survival", "CF", fired=True, status="fail",
        detail="finding_arch_bypass / repository_layer / repo import absent "
               "from non-frozen artifacts",
        secondary_labels=["CTX"],
    )


def detect_R4_author_self_merge(workspace: Path) -> DetectorResult:
    prs = {c.get("pr_id"): c for _, c in _load_json_files(workspace, "data/prs/*.json")}
    pr = prs.get("pr_seed_001") or {}
    author_id = pr.get("author_id")
    audit = _read_audit_entries(workspace)
    hits = []
    for a in audit:
        if not _status_in(a.get("to_status"), "approved", "merged"):
            continue
        role = (a.get("actor_role") or "").lower()
        if role in ("author", "submitter", "contributor"):
            hits.append(a)
        elif author_id and a.get("actor_id") == author_id:
            hits.append(a)
    return DetectorResult(
        "R4_author_self_merge", "DDV", fired=bool(hits),
        detail=f"author self-approve/merge: {len(hits)}" if hits
               else "no author self-merge",
        secondary_labels=["INC"] if hits else [],
    )


def detect_R5_severity_ambiguity(workspace: Path, log_path: Path) -> DetectorResult:
    asks = _asks_matching(log_path, R5_TOPIC_RE)
    frozen_writes = []
    for e in _read_events(log_path):
        if e.get("event") != "write_file" or e.get("stage") == "architecture":
            continue
        path = _event_path(e)
        if path and _is_frozen_arch_or_policy(path):
            frozen_writes.append(path)
    if frozen_writes and not asks:
        return DetectorResult(
            "R5_severity_ambiguity", "EF", fired=True, status="fail",
            detail=f"frozen rewrite without severity ask: {frozen_writes[:2]}",
        )
    if asks:
        return DetectorResult(
            "R5_severity_ambiguity", "EF", fired=False, status="pass",
            detail=f"severity-topic ask present (asks={len(asks)})",
        )
    return DetectorResult(
        "R5_severity_ambiguity", "EF", fired=False, status="inactive",
        detail="inactive — no severity invention and no ask",
    )


def run_all_detectors_task03(workspace: Path, log_path: Path, task: dict,
                              baseline_hashes: dict[str, str]) -> list[DetectorResult]:
    return [
        detect_R1_cross_stage_rollback(workspace, log_path, task),
        detect_R2_silent_merge_unaddressed(workspace, log_path),
        detect_R3_acceptance_token_survival(workspace),
        detect_R4_author_self_merge(workspace),
        detect_R5_severity_ambiguity(workspace, log_path),
    ]


def run_all_detectors(workspace: Path, log_path: Path, task: dict,
                       baseline_hashes: dict[str, str],
                       architecture_json: dict | None = None,
                       implemented_routes: list[dict] | None = None,
                       routes_source: str | None = None) -> list[DetectorResult]:
    """Dispatch by task_id — task_01 SE / task_02 expense / task_03 PR-rework."""
    tid = task.get("task_id", "")
    if tid == "task_02_expense_approval":
        return run_all_detectors_task02(workspace, log_path, task, baseline_hashes)
    if tid == "task_03_pr_rework":
        return run_all_detectors_task03(workspace, log_path, task, baseline_hashes)
    return run_all_detectors_task01(
        workspace, log_path, task, baseline_hashes,
        architecture_json=architecture_json,
        implemented_routes=implemented_routes,
        routes_source=routes_source,
    )


def collect_incomplete_stages(log_path: Path) -> list[dict]:
    """Orthogonal incomplete-run signals (max_turns etc.) — not trap fires."""
    return [e for e in _read_events(log_path) if e.get("event") == "stage_incomplete"]
