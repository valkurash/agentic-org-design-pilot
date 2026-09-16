"""
event_log.py — JSONL event logger. Field set matches org_spec.yaml
`logging.required_event_fields`: run, seed, cond, stage, agent, event,
domain, reasoning, refs, content_hash.

Full `content` is stored (knowability / INC vs CTX post-hoc). Optional
`output_preview` (first 200 chars) is a convenience for skim only — never
the sole copy of the payload.
"""
from __future__ import annotations
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone


class EventLogger:
    def __init__(self, log_path: Path, run: str, seed: int, cond: str,
                 model: str | None = None, temperature: float | None = None):
        # AUDIT_2026-07-22 N5: model/temperature stamped into every event so
        # the archived JSONL is self-describing (pilots ≤ 22 Jul lack these
        # fields — model for those known only from the runs/README ledger).
        self.log_path = Path(log_path)
        self.run = run
        self.seed = seed
        self.cond = cond
        self.model = model
        self.temperature = temperature
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self.log_path, "a")

    def log(self, *, stage: str, agent: str, event: str, domain: str = None,
            reasoning: str = None, refs: list[str] = None,
            content: str = None, extra: dict = None):
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16] if content else None
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "run": self.run,
            "seed": self.seed,
            "cond": self.cond,
            "model": self.model,
            "temperature": self.temperature,
            "stage": stage,
            "agent": agent,
            "event": event,
            "domain": domain,
            "reasoning": reasoning,
            "refs": refs or [],
            "content_hash": content_hash,
        }
        # Full payload — required for Puranam knowability / INC vs CTX audit.
        # Do not rely on output_preview alone (pilot_pair_01–02 truncations).
        if content is not None:
            record["content"] = content
            record["output_preview"] = content[:200]
        if extra:
            # extra must not strip full content if caller also passed preview
            for k, v in extra.items():
                if k == "output_preview" and "content" in record:
                    continue
                record[k] = v
        self._fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        self._fh.flush()

    def close(self):
        self._fh.close()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()
