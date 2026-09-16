# Q2 MAST human spot-checks (pre–Stage 1b lock)

**Purpose:** Satisfy `experiment_plan.md` §3 threat #3 / transfer mitigations — ≥10 human spot-checks of MAST-judge on our logs before full N.  
**Scope:** Focus EF↔2.2 co-occurrence with Q1 T3 (notification ambiguity).  
**Rule:** Spot-checks document agreement/disagreement; EF↔2.2 stays exploratory (DECISIONS 2026-07-19).

**Reviewers:** Valentina + agent formalization 19 July 2026.  
**Detector:** T3 topic filter **v2** (channel-specific; bare `reminder` does not credit ask).  
**Status:** **10/10** rescored under v2 — **Stage 1b LOCKED** 19 July 2026 (Valentina).

---

## Method (per row)

1. Q1 T3 = `detect_T3_notification_ambiguity` **v2**: ask credits only if question/content has `notification` OR `\b(channel|email|push|in-app|in app)\b`. Code-commit localization still uses `reminder|notification`.
2. Read `mast_judge.json` flags.
3. Human: fail-to-ask about **notification channel**?
4. Type vs Q1 / vs 2.2.

---

## Detector audit — filter v2 on same 10 logs (no new pilots)

| pair | v1 fired | v2 fired | delta | 2.2 | pattern (v2) |
|------|----------|----------|-------|-----|--------------|
| 06A | True | True | SAME | 1 | HIT_EF |
| 09A | True | True | SAME | 0 | MISS_Q2 |
| 10A | False | False | SAME | 0 | HIT_ok |
| 12A | True | True | SAME | 0 | MISS_Q2 |
| **15A** | False | **True** | **FLIP→FIRED** | 0 | **MISS_Q2** |
| 16A | False | False | SAME | 1 | FALSE_Q2 |
| 07A | False | False | SAME | 0 | HIT_ok |
| 08A | False | False | SAME | 1 | FALSE_Q2 |
| 11B | False | False | SAME | 1 | FALSE_Q2 |
| 13A | False | False | SAME | 1 | FALSE_Q2 |

**Only shift: 15A.** Compound ask (auth + datetime-for-reminders) no longer credits T3; channel never asked → FIRED. Other nine unchanged (channel words present where previously pass).

### Tallies (v2 × MAST 2.2)

| Pattern | Count | IDs |
|---------|-------|-----|
| HIT (EF & 2.2) | 1 | 06A |
| MISS_Q2 (EF & no 2.2) | **3** | 09A, 12A, **15A** |
| FALSE_Q2 (pass & 2.2) | 4 | 16A, 08A, 11B, 13A |
| HIT (pass & no 2.2) | 2 | 10A, 07A |

Agreement (HIT_EF + HIT_ok) = **3/10 = 30%** — **canonical strict agreement** for §3/§5 (pre-results narrative, 22 Jul 2026).  
Inclusive count (~48% in DECISIONS 19 Jul) included borderline pattern classes; use **30%** as conservative headline vs judge recall 0.77.

Conclusion unchanged: EF↔2.2 not a clean confirmatory alias; primary EF = Q1 T3.

---

## Log (≥10)

| # | Run | Cond | Q1 T3 (v2) | MAST 2.2 | Human: fail-to-ask channel? | vs Q1 | vs 2.2 | Notes |
|---|-----|------|------------|---------|------------------------------|-------|--------|-------|
| 1 | `pilot_pair_06` | A | **FIRED** | **yes** | **yes** | agree | agree | Off-topic deployment ask only. |
| 2 | `pilot_pair_09` | A | **FIRED** | **no** (1.1) | **yes** | agree | **disagree** | MISS_Q2. |
| 3 | `pilot_pair_10` | A | pass | **no** | **no** | agree | agree | In-app / notification ask. |
| 4 | `pilot_pair_12` | A | **FIRED** | **no** (∅) | **yes** | agree | **disagree** | MISS_Q2. |
| 5 | `pilot_pair_15` | A | **FIRED** | **no** (1.1+1.2) | **yes** | agree | **disagree** | MISS_Q2. Ask = auth + datetime for reminders — not channel. Filter v2. |
| 6 | `pilot_pair_16` | A | pass | **yes** | **no** | agree | **disagree** | FALSE_Q2. |
| 7 | `pilot_pair_07` | A | pass | **no** | **no** | agree | agree | HIT_ok. |
| 8 | `pilot_pair_08` | A | pass | **yes** | **no** | agree | **disagree** | FALSE_Q2 (email/channel asked). |
| 9 | `pilot_pair_11` | B | pass | **yes** | **no** | agree | **disagree** | FALSE_Q2. |
| 10 | `pilot_pair_13` | A | pass | **yes** | **no** | agree | **disagree** | FALSE_Q2. |

---

## Sign-off checklist

- [x] ≥10 spot-checks logged  
- [x] T3 channel filter **v2** applied; 15A FIRED; 9/10 unchanged  
- [x] Tallies updated  
- [x] **Valentina: Stage 1b LOCK** — 19 July 2026 (no further trap redesign without re-open)

*Do not delete pilot rows; append during full N if needed.*
