# Pre-registration summary (English)

**Signed:** 22–23 July 2026 (amended pre-registration before full N)  
**Addenda:** 24 July 2026 (task_03 instrument); 26 July 2026 (STOP paid runs / scope)  
**Author:** Valentina Kurashova  

This is an English summary of the signed memorandum. The confirmatory working-paper claim uses the scoped endpoint below.

**Terminology note.** In the working paper and [`DESIGN.md`](DESIGN.md), **Q1 / Q2** mean the dual *readout layers* on each run (Q1 = mechanical detectors on artifact state; Q2 = MAST LLM-as-judge). Below, **Slot 1 / 2 / 3** are the planned confirmatory *endpoints* in the Bonferroni family — not the same “Q1” as the detector layer.

## Confirmatory family (as amended)

Originally planned Bonferroni family **(c)** for escalation-failure endpoints:

| Slot | Cell | Endpoint |
|------|------|----------|
| Slot 1 | T3 (task_01) | fail-rate |
| Slot 2 | E2 (task_02) | terminal-resolution (pass vs non-pass) |
| Slot 3 | R2 (task_03) | terminal-resolution (pass vs non-pass) |

**Independent variable:** Condition A = instructed framework-default role/SOP prompts; Condition B = same plus machine-readable soft `org_spec` (rules named; violations still possible).

**Primary test (E2 / Slot 2):** exact McNemar on paired A/B seeds.

**Also-report / exploratory (not confirmatory):** structural-constraint floor checks; fabrication-desync on task_03; seed-claim completion rates.

## Scope after STOP (26 July 2026)

After calibration and the completed E2 full-N cell (n=18):

- **Sole confirmatory full-N endpoint reported in the working paper:** E2 (task_02 / Slot 2).
- **R2** (Slot 3) stayed at staged calibration (ceiling after reviewer resourcing); not run at full N.
- **T3** (Slot 1) stayed at small early sample + open keyword-detection gap; not run at full N.
- No claim of a completed three-cell Bonferroni family on three full-N cells.

Rationale (logged before further peeking at cancelled cells): after three packets and one soft confirmatory contrast, the informative next spend is stronger design levers (resources, enforcement, separated agents), not another soft full-N copy of the same design.

## Instrument note (task_03, pre–full N)

Before any task_03 full N, the reviewer stage was given write tools so “reviewer decides” could be measured on the PR object (packet v0.3). That change was instrument calibration, not a change to the confirmatory endpoint definitions.
