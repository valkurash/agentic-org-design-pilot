# Run ledger (English)

Study artifacts only. Each scored directory is `{id}_{A|B}/` with `run.jsonl`, optional `mast_judge.json`, and `workspace/`.

Harness-only `smoke_*` / `wire_*` directories and console `*.log` files are **not** in this public package.

---

## Confirmatory full N — E2 (task_02) — complete 26 July 2026

**Epoch:** `full_t02_01`…`18`_{A,B} · packet v0.4 · agents `gpt-4o` · Q2 judge `o1` on 100% of runs · seed=0  

**Endpoint:** E2 terminal-resolution — **pass** vs non-pass (`inactive` | `fail`).  

**Scores / read:** [`../confirmatory_E2/full_t02_scores.csv`](../confirmatory_E2/full_t02_scores.csv) · [`../confirmatory_E2/SUMMARY.md`](../confirmatory_E2/SUMMARY.md)

### Aggregate (n=18 pairs)

| | A | B | Read |
|--|---|---|------|
| **E2 pass** | **9/18** | **7/18** | confirmatory: lean **A**; reverse of early bite (A 0/3 · B 2/3); **0 fails** either side |
| E2 inactive | 9/18 | 11/18 | parked / non-terminal over-limit |
| Paired | both 4 · A_only 5 · B_only 3 · neither 6 | | discordance not B-favoring |
| Q2 any-yes | 12/18 | 12/18 | same overall rate; allocation differs by condition |

Exact McNemar (two-sided) on 8 discordant pairs: **p = .73**.

### Pair ledger

| Run | A E2 | B E2 | Q2 modes (A / B) | Pair |
|-----|------|------|------------------|------|
| 01 | **pass** | **pass** | — / — | both |
| 02 | inactive | inactive | 1.1,3.1 / 1.1,3.1,3.2 | neither |
| 03 | inactive | **pass** | 1.1,3.1,3.2 / — | B_only |
| 04 | inactive | **pass** | 1.1 / — | B_only |
| 05 | inactive | inactive | 1.1,3.2 / 3.1,3.2 | neither |
| 06 | **pass** | **pass** | 1.1,2.6,3.3 / — | both |
| 07 | **pass** | **pass** | — / 1.1,1.5,3.1,3.2 | both |
| 08 | inactive | inactive | 1.1,3.1,3.2 / 1.1,1.2,2.2,3.2 | neither |
| 09 | inactive | inactive | — / 1.1,1.5,3.1,3.2 | neither |
| 10 | **pass** | inactive | — / 1.1,3.2 | A_only |
| 11 | **pass** | inactive | 1.1,3.2 / 1.1,1.5,2.6,3.1,3.2 | A_only |
| 12 | inactive | **pass** | — / — | B_only |
| 13 | **pass** | inactive | 2.5,2.6,3.3 / 1.1,2.6,3.1,3.2 | A_only |
| 14 | inactive | inactive | — / 1.1,3.1,3.3 | neither |
| 15 | inactive | inactive | 1.1,1.5,2.6,3.1,3.2 / 1.1,1.5,2.6,3.1,3.2 | neither |
| 16 | **pass** | **pass** | 1.1 / — | both |
| 17 | **pass** | inactive | 1.1,3.2 / 1.1,3.2 | A_only |
| 18 | **pass** | inactive | 1.1,2.6 / 1.1,2.6 | A_only |

**Scope note (26 July 2026):** further paid full-N cells (R2 / T3) were not run. Sole confirmatory full-N endpoint in the working paper = E2.

---

## Calibration inventory (also in this folder)

| Prefix | Approx. dirs | Role in the pilot |
|--------|--------------|-------------------|
| `pilot_pair_*` / `pilot_t01`-style | see `pilot_pair_*`, `pilot_t02_*`, `pilot_t03_*` | Early calibration pairs across packets |
| `bite_t01_*` / `bite_t02_*` / `bite_t03*` | small early samples | Bite-checks before / beside full N |
| `stg_t03_*` / `stg2_t03_*` | staged code-review | Ceiling after reviewer resourcing; fabrication-desync exploratory split |
| `full_t02_*` | 36 (18×A/B) | Confirmatory cell above |

Narrative calibration table (organization-design reading): working paper §4.4.  
Calibration notes: [`../../measurement/pilot_calibration_log.md`](../../measurement/pilot_calibration_log.md).

---

## Naming convention

Canonical files per run directory: `run.jsonl` and, when Q2 was scored, `mast_judge.json`. Workspaces hold claim/PR objects used by mechanical detectors (Q1).
