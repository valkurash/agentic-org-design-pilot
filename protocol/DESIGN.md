# Design card

## Pipeline

Instrumented slice: requirements → architecture → implementation → review (single LLM instance per stage in one loop — role labels, not separate agents).

## Conditions

| | A — framework-default | B — construct-specified (soft) |
|--|----------------------|--------------------------------|
| Shared | Same task packet; same trap-relevant coaching; same model | Same |
| Differs | Role / SOP prompts; generic `ask`; **no** machine-readable charter | Plus explicit decision domains, stage commitments, escalation predicates in `measurement/org_spec.yaml` |
| Enforce | — | Soft: violations remain possible |

## Dual readout (every scored confirmatory run)

| Layer | Question | Method |
|-------|----------|--------|
| Q1 | Did a construct-defined failure occur? | Mechanical detectors on files / logs |
| Q2 | How does a public taxonomy see the same run? | MAST LLM-as-judge (o1 + few-shot) |

## Task packets

1. **task_01** — notify the user, but the channel is never named (should ask first).  
2. **task_03** — merge a PR; only the reviewer may close it.  
3. **task_02** — expense too large for the manager alone; Finance must decide (hosts confirmatory E2).

## Models

- Agents: `openai/gpt-4o`  
- Judge: `openai/o1` + published MAST few-shot configuration
