# Agentic organization-design pilot — replication package

**Author:** Valentina Kurashova  
**Date:** August 2026 · working-paper framing revised 15 September 2026 (data and results unchanged)  

Open materials for a pilot study on **operationalizing organization-design constructs** in human–AI–agent software workflows: measurement instrument, task packets, stand code, pre-registered confirmatory comparison, and full run logs.

This repository is a **replication package**, not a private research notebook. It includes the pilot working paper (prior work to a field-first doctoral programme; not its first stage) plus everything needed to inspect and re-score the pilot evidence.

## Documents

| File | Description |
|------|-------------|
| [`paper/working_paper.md`](paper/working_paper.md) | Pilot working paper (markdown) |
| [`paper/Kurashova_Working_Paper.pdf`](paper/Kurashova_Working_Paper.pdf) | Same working paper (PDF) |
| [`protocol/PRE_REGISTRATION.md`](protocol/PRE_REGISTRATION.md) | English summary of the signed pre-registration / scope |
| [`protocol/DESIGN.md`](protocol/DESIGN.md) | Short design card (conditions, endpoints, models) |
| [`results/runs/README.md`](results/runs/README.md) | English run ledger (E2 table + calibration inventory) |

## Confirmatory result (headline)

**Cell:** task_02 expense escalation · soft construct charter (B) vs instructed framework-default (A) · n=18 paired seeds.

| | Condition A | Condition B |
|--|-------------|-------------|
| Finished (pass) | 9/18 | 7/18 |
| Unfinished | 9/18 | 11/18 |
| Wrongful approve | 0/18 | 0/18 |

Exact McNemar (two-sided) on 8 discordant pairs: **p = .73**. Soft naming did not raise finish rates. See [`results/confirmatory_E2/SUMMARY.md`](results/confirmatory_E2/SUMMARY.md) and [`results/confirmatory_E2/full_t02_scores.csv`](results/confirmatory_E2/full_t02_scores.csv).

**Models pinned:** agents `openai/gpt-4o`; MAST judge `openai/o1` (few-shot).

## How to re-score the confirmatory cell

```bash
cd code
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Point score_runs at results/runs/full_t02_* — see code/README.md for path notes
python score_runs.py --help
```

You do **not** need an API key to re-score existing `run.jsonl` + workspace claim files. A key is required only to *re-run* agents or the MAST judge.

## Layout

```
paper/           working paper (md + PDF)
protocol/        pre-registration summary + design card
measurement/     codebook, theory notes (P1–P7), org_spec.yaml, MAST judge assets
tasks/           task_01–03 packets + fixtures
code/            full stand (detectors, MAST adapter, scoring, run_pair, …)
results/
  confirmatory_E2/   SUMMARY + scores for the n=18 cell
  runs/              study run directories (full workspaces) + English ledger
```

**Excluded from this package:** upstream MAST-Data epidemiology dump (~63MB); ephemeral harness dirs (`smoke_*`, `wire_*`); console `*.log` files.

## License

Code and documentation in this package: **MIT** (see [`LICENSE`](LICENSE)).  
Third-party materials (e.g. MAST judge assets) retain their upstream licenses; see `measurement/mast/`.

## Contact

Valentina Kurashova — `valkurash@gmail.com`  
Questions about this package or the research welcome at that address.
