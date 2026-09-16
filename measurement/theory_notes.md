# Theory notes — sources, metrics, measurement model

**Updated:** 17 July 2026  
**Labels / crosswalk:** [`codebook.md`](codebook.md) · **Pipeline:** [`../protocol/DESIGN.md`](../protocol/DESIGN.md)

---

## 1. Methodological license

Puranam (Microstructure Ch.9, p.165): goal-directed multi-agent groups = **synthetic organizations** — valid test-bed. Claim = *sufficiency of mechanism* (p.166).

---

## 2. Constructs (literature)

| Construct | Source | pp. |
|-----------|--------|-----|
| Organization | Puranam | 3–4 |
| Division of labor | Puranam | 10, 45–46 |
| Integration of effort | Puranam | 9, 68–70 |
| Coordination failure | Puranam | 70–71 |
| Authority / escalation | Puranam Ch.5 | 93–99 |
| Cognitive reapportionment | Konsynski, Kathuria & Karhade 2024 | 5–12 |
| Boundaries / misfits | Simon; Henkel 2023 | — |

---

## 3. Labels & propositions

### 3.1 Labels → constructs

| Label | Construct | Puranam type |
|-------|-----------|--------------|
| INC, CF, CTX | Integration | omission |
| DDV | Division + authority | commission |
| EF, OE | Authority; KKK reapportionment | — |
| RW | Rework symptom | gated (P4) |
| SK, SG, CP | Controls | — |
| ρ | Integration aggregate | scalar (p.91) |

### 3.2 P1–P7 (WP empirical set)

| P | Claim (plain) | How tested (one study) |
|---|---------------|------------------------|
| P1 | Dependent work needs handoff rules | INC + CF + CTX (detectors / ρ) A vs B |
| P2 | Didn't know ≠ disobeyed | `input_context_refs` → INC vs CF/CTX |
| P3 | Own your domain; escalate the rest | DDV, EF detectors |
| P4 | Exploration ≠ defect | RW counting rule |
| P5 | Ambiguity → ask first | EF detector on ambiguity trap |
| P6 | Info lost at handoffs | CTX, CF on constraint-survival trap |
| P7 | Frozen interfaces reduce breaks | INC on freeze / interface traps |

**Dropped (2026-07-17):** P8 (structure × MAST-Data profiles) — MAST already argues org design; WP tests **intervention**, not re-prediction on public traces.

**Examples:** P1 two cooks / one pot · P2 milk unknown vs ignored · P7 frozen auth module.

### 3.3 Framework-default vs construct-operationalized

Same pipeline stages and task packet; two coordination designs.

**Framework-default (Condition A).** Software-company **role templates** (PM, Architect, Engineer, Reviewer). Roles and chat order exist; explicit coordination rules do not. Decision rights implicit; handoff = prior text; no designed “stop and ask.”

**Construct-operationalized (Condition B).** Same stages + rules in `org_spec.yaml`: decision domains; handoff commitments; escalation predicates.

**Compare** = paired A/B; every run answers **Q1** (detectors) and **Q2** (MAST / other external judges); report both + exploratory co-occurrence. Disagreement protocol in [`../protocol/DESIGN.md`](../protocol/DESIGN.md) §1.

---

## 4. Measurement model

```
Theory (P1–P7) → label names → planted traps → mechanical detectors → A vs B rates
                                                      ↓ optional
                                              MAST judge on our traces
```

| Layer | Role | Example |
|-------|------|---------|
| **Mechanical detector** | Primary outcome — scripted true/false | `auth/**` changed → INC on T1 |
| **Construct label** | Theory name for that failure | INC = commitment violation |
| **MAST mode (secondary)** | Literature-comparable symptom | EF trap ↔ expect ↓ mode 2.2 |
| **P** | Hypothesis | “P5: B has fewer EF on ambiguity trap” |

### Literature → construct → label → P → detector

| Literature | Construct | Labels | P | Detector type |
|------------|-----------|--------|---|---------------|
| Puranam 68–74 | Integration | INC, CF, CTX | P1, P2, P6 | diff / grep / context refs |
| Puranam 93–99; KKK | Decision rights / reapportionment | DDV, EF | P3, P5 | domain check / `ask` event |
| Henkel / interfaces | Design rules | INC | P7 | freeze / interface diff |
| Puranam 68–89 | Search vs execution | RW | P4 | mode gate |

### How each P is tested

| P | Statistic | Supported if |
|---|-----------|--------------|
| P1 | INC+CF+CTX (or ρ) per run, A vs B | Lower in B |
| P2 | CF/CTX vs INC via logged context | Split consistent with detectors |
| P3 | DDV + EF rate | Lower in B |
| P4 | RW count | Search iterations excluded |
| P5 | EF on ambiguity trap | Lower in B |
| P6 | CTX+CF on boundary trap | Lower in B |
| P7 | INC on freeze / interface trap | Lower in B |

### Validation status

| Step | Status |
|------|--------|
| Spec (constructs → labels → P → detectors) | ✅ |
| One-study A/B + detectors | 🔴 |
| MAST judge on every run + co-occurrence with detectors | 🔴 |
| Optional κ on secondary labels | ⚪ |

---

## 5. MAST (related measurement, not a second study)

Same problem space (why MAS fail); different layer:

| | MAST | This WP |
|---|------|---------|
| Layer | Symptom taxonomy | Org-design mechanisms + intervention |
| Unit | Trace flags `1.1`–`3.3` | Detector fires per trap; **Q2** MAST flags on *our* runs |
| Scale | 1242 public traces | Paired A/B on instrumented slice |

**Cite in §2:** MAST finds structural/coordination failures dominate; org design analogy (Perrow / HRO). We do **not** re-test that claim on their corpus. We use it as epidemiology context and as **required Q2** external readout on our stand (same runs as Q1).

**Crosswalk (trap design + Q2 co-occurrence):** 2.2↔EF · 1.4/2.1↔CTX · 1.2↔DDV · 2.3↔CF (sometimes INC) · 2.5↔INC/CTX — full table in [`codebook.md`](../experiment/codebook.md) §2.


**WP claim:** MAST = ally baseline; we add **construct operationalization + causal A/B**.

---

## 6. Other sources

Hevner 2004 · Henkel 2023 · Simon (boundaries).
