# Stand code

Full copy of the pilot stand (requirements → architecture → implementation → review).

| Module | Role |
|--------|------|
| `run_pair.py` | CLI: run one A/B pair |
| `detectors.py` | Q1 mechanical scorers |
| `mast_adapter.py` | Q2 MAST judge adapter |
| `score_runs.py` | Batch score existing run directories |
| `org_spec_loader.py` | Load org_spec / task packets |
| `prompts.py` | Condition A vs B prompts |
| `graph.py` | Stage loop |
| `llm_client.py` | OpenRouter / Anthropic / mock |

## Paths in this package

- `org_spec.yaml` → `../measurement/org_spec.yaml`
- task YAMLs → `../tasks/`
- MAST definitions → `../measurement/mast/`
- run directories → `../results/runs/`

Symlink or edit paths if a script still assumes the private-repo layout (`../org_spec.yaml` next to `stand/`).

## Secrets

Do **not** commit `.env`. API keys are required only for *live* re-runs, not to inspect existing logs.
