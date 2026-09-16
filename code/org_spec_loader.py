"""
org_spec_loader.py — parses experiment/org_spec.yaml into objects the graph
and the detectors can both query. No LLM calls here; pure data.
"""
from __future__ import annotations
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from fnmatch import fnmatch


@dataclass
class Role:
    name: str
    agent_id: str
    domains: list[str]
    may_not_decide: list[str]


@dataclass
class EscalationPredicate:
    id: str
    rule: str
    action: str


@dataclass
class OrgSpec:
    schema_version: str
    enforcement_mode: str
    stages: list[str]
    roles: dict[str, Role]
    commitments: dict
    predicates: dict[str, EscalationPredicate]
    frozen_modules: list[str]
    raw: dict

    def role_for_stage(self, stage: str) -> Role:
        return self.roles[stage]

    def domain_owner(self, domain: str) -> str | None:
        for stage, role in self.roles.items():
            if domain in role.domains:
                return stage
        return None

    def is_in_domain(self, stage: str, domain: str) -> bool:
        return domain in self.roles[stage].domains

    def touches_frozen(self, path: str) -> bool:
        return any(fnmatch(path, glob) for glob in self.frozen_modules)

    def required_fields(self, stage: str) -> list[str]:
        return self.commitments.get(stage, {}).get("required_fields", [])


def load_org_spec(path: str | Path) -> OrgSpec:
    raw = yaml.safe_load(Path(path).read_text())

    roles = {}
    for stage, r in raw["roles"].items():
        roles[stage] = Role(
            name=stage,
            agent_id=r["agent_id"],
            domains=r.get("domains", []),
            may_not_decide=r.get("may_not_decide", []),
        )

    predicates = {}
    for p in raw["escalation"]["predicates"]:
        predicates[p["id"]] = EscalationPredicate(
            id=p["id"], rule=p["rule"], action=p["action"]
        )

    # frozen_modules can live under org_spec (not always) — task packet also
    # supplies its own; loader here only reads org_spec-level ones if present.
    frozen = []
    arch_commit = raw.get("commitments", {}).get("architecture", {})
    if "frozen_modules" in arch_commit.get("required_fields", []):
        pass  # frozen_modules content is per-task, injected at run time — see task_loader

    return OrgSpec(
        schema_version=raw["schema_version"],
        enforcement_mode=raw["enforcement_mode"],
        stages=raw["organization"]["stages"],
        roles=roles,
        commitments=raw["commitments"],
        predicates=predicates,
        frozen_modules=frozen,  # populated later via .set_frozen_modules()
        raw=raw,
    )


def load_task(path: str | Path) -> dict:
    """Load a task packet (e.g. task_01_todo_reminders.yaml)."""
    return yaml.safe_load(Path(path).read_text())


if __name__ == "__main__":
    import sys
    spec = load_org_spec(sys.argv[1] if len(sys.argv) > 1 else
                          "../org_spec.yaml")
    print("stages:", spec.stages)
    print("enforcement_mode:", spec.enforcement_mode)
    for stage, role in spec.roles.items():
        print(f"  {stage} ({role.agent_id}): domains={role.domains}")
    print("domain_owner('interfaces') ->", spec.domain_owner("interfaces"))
    print("is_in_domain('code', 'scope') ->", spec.is_in_domain("code", "scope"))
