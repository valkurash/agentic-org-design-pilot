# MAST helpers (§2 epidemiology + Q2 judge assets)

Public [MAST-Data](https://huggingface.co/datasets/multi-agent-systems-failure-taxonomy/MAST-Data) tools and judge materials. **Not** a second WP study.

| Path | Role |
|------|------|
| `count_se_slice.py` | Corpus + ProgramDev SE-slice → `data/summary/se_slice_stats.json` |
| `data/raw/MAST-Data/` | Local download (gitignored) |
| `data/summary/` | Cached stats for §2 (1242 / 390) |
| `definitions.txt` · `examples.txt` | From MAST repo — used by [`../stand/mast_adapter.py`](../stand/mast_adapter.py) (Q2) |

**Caution:** `MAD_human_labelled_dataset.json` (IAA rounds) uses an **older ~18-mode** scheme — not the final 14-mode `mast_annotation`. Do not use it as-is for ≥10 spot-checks against the Q2 judge (see stand README / DECISIONS).

WP experiment A/B: [`../org_spec.yaml`](../org_spec.yaml), [`../tasks/`](../tasks/), [`../stand/`](../stand/).
