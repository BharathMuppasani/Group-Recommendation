# Implementation Plan: Group Recommendation for Proposal → Team Formation

## 0) Goal

Build a team recommender that, given proposals and researchers:

* prioritizes **rare skills**
* penalizes **redundant skills via diminishing returns**
* selects teams using **greedy marginal gains**
* stops based on **proposal coverage**, not per-candidate thresholds

All runs must generate **minimal Markdown reports** under `reports/`.

---

## 1) Plan Phase (must be done before coding)

Create the following file:

### `reports/00_plan.md`

Include:

* Objective (1–2 lines)
* Key assumptions (binary skills in v1, proposal-relevant scoring only)
* Method summary (rarity weights + diminishing returns + greedy selection)
* Definition of “done” (CLI works, tests pass, reports generated)

---

## 2) Environment Setup

### 2.1 Create repository

```bash
mkdir group-reco && cd group-reco
git init
```

### 2.2 Conda environment

```bash
conda create -n groupreco python=3.11 -y
conda activate groupreco
```

### 2.3 Install dependencies

```bash
pip install numpy pandas pydantic typer rich pytest
```

### 2.4 Freeze requirements

```bash
pip freeze > requirements.txt
```

---

## 3) Project Structure (mandatory)

```
group-reco/
  README.md
  requirements.txt
  data/
    sample/
      proposals.json
      researchers.json
  reports/
    00_plan.md
    01_data_summary.md
    02_run_report.md
    03_tests.md
  src/
    groupreco/
      __init__.py
      config.py
      io.py
      weighting.py
      scoring.py
      greedy.py
      metrics.py
      cli.py
  tests/
    test_weighting.py
    test_greedy.py
    test_end_to_end.py
```

---

## 4) Corrected Methodology (core logic to implement)

### 4.1 Skill rarity weights

Compute skill weights from researcher pool:

Let:

* `N` = number of researchers
* `df(s)` = number of researchers with skill `s`

Weight:

[w(s) = \log\left(\frac{N+1}{df(s)+1}\right)]

Optional: normalize weights to `[0,1]`.

---

### 4.2 Proposal Seat_Cost (reporting only)

[seat_cost(p) = \frac{1}{|R_p|}\sum_{s\in R_p} w(s)]

**Do NOT use Seat_Cost as a candidate selection threshold.**
It is only a proposal difficulty indicator.

---

### 4.3 Team objective with diminishing returns

Coverage count:

* `c_T(s)` = number of team members covering skill `s`

Coverage gain:
[g(c) = 1 - \alpha^c \quad (\alpha = 0.5 \text{ default})]

Team score:
[F(T,p) = \sum_{s \in R_p} w(s) \cdot g(c_T(s))]

Marginal gain:
[\Delta(i|T,p) = F(T \cup {i}, p) - F(T, p)]

Compute gains **only over proposal-required skills**.

---

### 4.4 Greedy team selection

For each proposal:

1. Initialize empty team `T`
2. Repeat:

   * Compute marginal gain for all remaining candidates
   * Select candidate with max gain
   * Stop if:

     * team size ≥ `max_team_size`, OR
     * coverage ≥ `coverage_target` (e.g. 0.9), OR
     * best marginal gain < `min_gain`
3. Return team and diagnostics

---

### 4.5 Coverage metric (stopping rule)

[coverage(T,p) =
\frac{\sum_{s\in R_p} w(s)\cdot \mathbf{1}[c_T(s)\ge 1]}
{\sum_{s\in R_p} w(s)}]

---

## 5) Sample Data (for v1 testing)

### `data/sample/proposals.json`

```json
[
  {
    "id": "p1",
    "name": "Health NLP",
    "required_skills": ["nlp", "healthcare", "python", "ml"]
  },
  {
    "id": "p2",
    "name": "Robotics Planning",
    "required_skills": ["ros2", "planning", "python", "rl", "simulation"]
  }
]
```

### `data/sample/researchers.json`

```json
[
  {"id":"r1","name":"Asha","skills":["python","ml","nlp"]},
  {"id":"r2","name":"Ben","skills":["ros2","simulation","python"]},
  {"id":"r3","name":"Chen","skills":["planning","rl","python"]},
  {"id":"r4","name":"Dia","skills":["healthcare","nlp","ux"]},
  {"id":"r5","name":"Eli","skills":["databases","backend","python"]}
]
```

---

## 6) Module Responsibilities

### `io.py`

* Load and validate JSON
* Basic sanity checks

### `weighting.py`

* Compute skill rarity weights

### `scoring.py`

* Seat cost
* Coverage ratio
* Team score
* Marginal gain

### `greedy.py`

* Core greedy team builder
* Iterative marginal gain recomputation

### `metrics.py`

* Final coverage
* Uncovered skills
* Redundancy statistics

### `cli.py`

Typer CLI:

```bash
groupreco run \
  --data data/sample \
  --alpha 0.5 \
  --max-team-size 5 \
  --coverage-target 0.9
```

---

## 7) Reports (Markdown only)

### `reports/01_data_summary.md`

* # proposals / researchers
* Rarest skills
* Seat cost per proposal
* Missing-skill warnings

### `reports/02_run_report.md`

For each proposal:

* Required skills
* Seat cost
* Selected team (ordered)
* Final coverage
* Uncovered skills
* Iteration log (pick, gain, coverage)

### `reports/03_tests.md`

* Tests executed
* Pass/fail summary
* Edge cases found

---

## 8) Testing Plan

### Unit tests

* Rarity weights behave correctly
* Diminishing returns reduce marginal gain
* No duplicate team members

### End-to-end test

* Load sample data
* Build team
* Coverage increases monotonically
* Report files generated

Run:

```bash
pytest -q
```

---

## 9) Agent Autonomy Guidelines

* Follow the corrected methodology strictly
* Prefer clarity over optimization
* Keep code modular and testable
* Always generate Markdown reports
* Leave TODOs for future extensions (proficiency, constraints, fairness)

---

## 10) Future Extensions (DO NOT implement in v1)

* Skill proficiency levels
* Hard constraints per proposal
* Budget-aware team size
* Multi-objective optimization
* Skill ontology / synonym handling
