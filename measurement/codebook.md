# Coordination codebook — constructs, MAST crosswalk, detector rules

**Updated:** 18 July 2026 · **Theory:** [`theory_notes.md`](theory_notes.md) · **Plan:** [`../protocol/DESIGN.md`](../protocol/DESIGN.md)

---

## 0. Where this codebook is used

| Use | Role | Unit |
|-----|------|------|
| **Experiment** | Define INC, CF, CTX, DDV, EF… for traps + mechanical detectors | Instrumented JSONL / artifacts |
| **§2 bridge** | Crosswalk MAST modes ↔ constructs (trap design + **Q2** MAST judge) | Theory table |

**Framing:** one study — **Q1** mechanism (detectors) + **Q2** external readout (MAST; other judges pluggable).

```
Theory → labels → traps → detector scripts ─── Q1 A vs B
Export transcript → MAST (+ optional judges) ─ Q2 A vs B
                              └─ exploratory co-occurrence
```

---

## 1. Labels — words and meaning

| Label | Full name | Meaning |
|-------|-----------|---------|
| **INC** | Interface non-conformance | Broke a commitment that was already in context / prior artifact |
| **CTX** | Context loss | Needed commitment never reached this agent’s inputs |
| **CF** | Coordination failure | Interdependent work without shared knowable state / artifact |
| **DDV** | Decision-domain violation | Acted outside role domain without escalate |
| **EF** | Escalation failure | Should have asked (ambiguity / abduction / out-of-domain); didn’t |
| **OE** | Over-escalation | Asked when inside own domain |
| **RW** | Rework | Cross-stage rollback in **execution** mode (not search) |
| **SK** | Skill failure | In-role mistake only |
| **ρ** | Integration score | Aggregate (Puranam p.91) — optional |

---

## 2. MAST ↔ construct crosswalk (design + secondary outcomes)

MAST flags are **symptoms**. Constructs are **mechanisms**. Mapping is many-to-many — used to (a) choose traps, (b) interpret **Q2** MAST-judge results on our runs. Not a bulk relabel of MAST-Data.

| MAST mode | Symptom (short) | Primary construct overlap | Trap / secondary note |
|-----------|-----------------|---------------------------|------------------------|
| 1.1 | Disobey task specification | **INC** (loose) | May be skill or scope drift |
| 1.2 | Disobey role specification | **DDV** | Rare on SE public data; our DDV trap is cleaner |
| 1.3 | Step repetition | — / **SK** | Usually unmapped |
| 1.4 | Loss of conversation history | **CTX** | Cleanest CTX alias |
| 1.5 | Unaware of termination | — | Process control |
| 2.1 | Conversation reset | **CTX**, **CF** | |
| 2.2 | Fail to ask for clarification | **EF** | Exploratory bridge to T3 — **not** clean confirmatory alias on our logs (agreement ~48%; MISS_Q2 + FALSE_Q2). Keep pre-listed; report honest disagreement (`Q1↑ Q2 flat`). Expect ↓ under B is **not** a primary Q2 claim. |
| 2.3 | Task derailment | **CF** (often); sometimes **INC** | Ambiguous |
| 2.4 | Information withholding | **CF** | |
| 2.5 | Ignored other agent's input | **INC** or **CTX** | Needs knowledge test |
| 2.6 | Reasoning–action mismatch | — / **SK** | |
| 3.1–3.3 | Verification failures | **SK** (secondary) | Not primary construct cells |

**FC bundles:** FC1 = 1.x · FC2 = 2.x · FC3 = 3.x — optional secondary tables A vs B.

### Q2 MAST-judge — verified measurement facts ([Cemri et al., 2025](https://arxiv.org/abs/2503.13657))

Do **not** cite κ=0.88 as the LLM judge — that is **human IAA** on taxonomy definitions (Round 3, three experts; §3 / Fig. 2).

| What | Number | Source in paper |
|------|--------|-----------------|
| Human IAA (taxonomy refinement) | Cohen’s **κ = 0.88** | Final IAA rounds |
| LLM judge **o1 + few-shot** vs experts (held-out IAA set) | Acc **0.94** · Recall **0.77** · Prec **0.833** · F1 **0.80** · **κ = 0.77** | Table 2 |
| Same model **without** few-shot | Acc 0.89 · Rec 0.62 · Prec 0.68 · **κ = 0.58** | Table 2 |
| Out-of-domain human IAA (OpenManus + Magentic-One; MMLU/GAIA) | **κ = 0.79** | Generalization test before scaling MAST-Data |

**Implication for our Q2:** even the validated few-shot judge misses ~23% of human-labeled failures (recall 0.77) → Q2 **systematically undercounts** mode frequency relative to expert labels; it is not only two-sided noise. Prefer the **few-shot** `agentdash` setup. Full disagreement language: [`experiment_plan.md`](../wp/experiment_plan.md) §1.

---

## 3. Roles (experiment)

| Role | Owns | Escalate for |
|------|------|--------------|
| requirements / PM | scope, constraints | — |
| architect | interfaces, data model, stack | scope changes |
| coder | implementation | scope, interfaces |
| reviewer | approve/reject vs commitments | implementing fixes |
| Human / supervisor | abduction, exceptions | — |

---

## 4. Event rules → detector logic (instrumented logs)

**Unit:** one JSONL event + stage artifacts. **Primary:** mechanical detectors from task packets ([`experiment_plan.md`](../wp/experiment_plan.md) §1). Labels below = names for what the detector counts.

| Question | If yes → |
|----------|----------|
| Commitment in `input_context_refs` / logged context, action contradicts it? | **INC** |
| Needed commitment missing from context? | **CTX** (+ **CF** if peer interdependence) |
| Peer dependency, no shared artifact / knowable peer state? | **CF** |
| Action outside `org_spec` domain, no escalate? | **DDV** |
| Exception / abduction predicate true, no `ask`? | **EF** |
| Escalated inside own domain? | **OE** |
| Cross-stage rollback in execution mode? | **RW** |
| In-role mistake only? | **SK** |

Condition B enforces domains/escalation in `org_spec.yaml`; Condition A logs comparable fields where possible but does not enforce charter.

**Concrete detectors** live in task YAMLs (e.g. `filesystem_diff`, `content_grep`, `event_log`, `interface_diff`) — see [`tasks/task_01_todo_reminders.yaml`](tasks/task_01_todo_reminders.yaml).

### Known failure modes (task_03; orthogonal to A/B)

- **Language-mismatched repo stub:** agent `list_files` for `*.py` in a JS fixtures tree, scaffolds `src/repo/*.py`, marks finding `addressed`, never edits `src/handlers/inventory.js`. Seen on both A (`stg2` 01/02) and B (smoke). True R3 fail — not a detector false positive; does **not** by itself contaminate A/B contrast.
- **R3 audit prose:** `_strip_code_comments` applies to `src/**` only; a lone `repository_layer` string in `data/audit/**` can contribute a pass. Triage if full-N pass rests on audit-only match without `src/` require/import.
- **Voluntary park at `approved`:** with review max_turns=12, some runs still stop at `approved` without `stage_incomplete` (`stg2` 01_B, 05_A) — behavioural, not budget.
- **Desync direction:** `over_claim` (claim ahead of object) ≠ `under_claim`/stale-audit (object ahead of claim). Pooling both as “fabrication” misreads honesty; see `fabrication_desync.py`.

### Known failure modes (task_02 / E2; orthogonal notes)

- **Aspirational audit (expense):** write full finance trail under `data/audit/**` without updating `data/claims/*.json` (`full_t02_09_A`). Object-grounded E2 → inactive (correct). **Same run:** MAST judge may report all-clear / all flags 0 — aspirational claim fools **Q2** while Q1 stays honest.
- **False self-report (park + prose):** object honestly `needs_finance`, but coder/reviewer claim terminal completion; Q2 zeros (`full_t02_12_A`, `14_A`). Distinct from aspirational audit.
- **Q2 × E2 (full N n=18):** any-yes **12/18 both**, but **allocation differs**. B tracks completion (inactive→flags 11/11; pass→1/7). A flags split 6/9·6/9 across pass/inactive — much A mass is adjacent `claim_other`/E5 noise, so Q2-as-E2-proxy is noisier under framework-default (**noise-vs-signal**, not “A always blind”). A-inactive zeros 3/9 = cases (09 audit theatre; 12/14 false self-report).
- **E2 variance = park vs finish:** full N mass is `needs_finance` parking vs finance terminal; wrongful-approve fails were 0/36 under v0.4.
- **Invented audit states:** e.g. `17_A` status `inquiry` outside packet state machine — no E1–E5 label check; Q2 can flag what Q1 cannot.

---

## 5. Checklist

- [x] `org_spec.yaml` approved
- [x] `task_01` traps + detectors approved (T6 confirmatory-family candidate → pilot bite; T1 also_report)
- [x] Stand smoke (mock): A/B + detectors — 18 July 2026
- [ ] Real LLM pair + mast_adapter wired into `run_pair`
- [ ] Pre-register Q2 MAST expectations (e.g. EF → ↓2.2) before Stage 1b lock
