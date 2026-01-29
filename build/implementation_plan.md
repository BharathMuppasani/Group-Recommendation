# Implementation Plan - Group Recommendation System

This plan outlines the steps to build the `group-reco` system as defined in `prompt.md`. The goal is to build a team recommender that prioritizes rare skills and uses greedy marginal gains with diminishing returns.

## User Review Required

> [!IMPORTANT]
> This plan follows the strict specificiation in `prompt.md`.
> - **Environment**: Will use `python=3.11`.
> - **Methodology**: Strict adherence to the `w(s)` and `F(T,p)` formulas provided.
> - **Output**: Markdown reports in `reports/`.

## Proposed Changes

### Project Setup
#### [NEW] [Structure Setup]
- Initialize git repository.
- Create directory structure: `data/sample`, `reports`, `src/groupreco`, `tests`.
- Create `requirements.txt` with: `numpy`, `pandas`, `pydantic`, `typer`, `rich`, `pytest`.

### Documentation & Planning
#### [NEW] [reports/00_plan.md](file:///Users/bittu/Desktop/projects/group-reco/reco_new-method/group-reco/reports/00_plan.md)
- Create the mandatory planning document with objective, assumptions, and method summary.

### Data Management
#### [NEW] [data/raw/m2_proposal_skills.csv](file:///Users/bittu/Desktop/projects/group-reco/reco_new-method/group-reco/data/raw/m2_proposal_skills.csv)
- Real proposals data (CSV).
#### [NEW] [data/raw/m2_researcher_skills.csv](file:///Users/bittu/Desktop/projects/group-reco/reco_new-method/group-reco/data/raw/m2_researcher_skills.csv)
- Real researchers data (CSV).

### Source Code (`src/groupreco/`)
#### [NEW] [__init__.py](file:///Users/bittu/Desktop/projects/group-reco/reco_new-method/group-reco/src/groupreco/__init__.py)
#### [NEW] [config.py](file:///Users/bittu/Desktop/projects/group-reco/reco_new-method/group-reco/src/groupreco/config.py)
- Define configuration constants (e.g., alpha, formatting).
#### [NEW] [io.py](file:///Users/bittu/Desktop/projects/group-reco/reco_new-method/group-reco/src/groupreco/io.py)
- Pydantic models for `Researcher` and `Proposal`.
- Functions to load and validate JSON data.
- **[UPDATE]** Add CSV loading support (`load_researchers_csv`, `load_proposals_csv`).
- **[UPDATE]** Implement robust parsing for "set-string" skill columns (e.g., `"{'skill1', 'skill2'}"`).
#### [NEW] [weighting.py](file:///Users/bittu/Desktop/projects/group-reco/reco_new-method/group-reco/src/groupreco/weighting.py)
- Implement `calculate_rarity_weights(researchers)` using the log formula.
#### [NEW] [scoring.py](file:///Users/bittu/Desktop/projects/group-reco/reco_new-method/group-reco/src/groupreco/scoring.py)
- Implement `calculate_seat_cost`.
- Implement `calculate_team_score` (diminishing returns).
- Implement `calculate_marginal_gain`.
#### [NEW] [greedy.py](file:///Users/bittu/Desktop/projects/group-reco/reco_new-method/group-reco/src/groupreco/greedy.py)
- Implement `GreedyOptimizer` class or function.
- Loop for candidate selection based on marginal gain.
#### [NEW] [metrics.py](file:///Users/bittu/Desktop/projects/group-reco/reco_new-method/group-reco/src/groupreco/metrics.py)
- Implement coverage calculation and stats.
#### [NEW] [cli.py](file:///Users/bittu/Desktop/projects/group-reco/reco_new-method/group-reco/src/groupreco/cli.py)
- Implement Typer app with `run` command.
- Argument parsing: `--data`, `--alpha`, `--max-team-size`, `--coverage-target`.
- Orchestrate loading, weighting, optimization, and reporting.

### Tests
#### [NEW] [tests/test_weighting.py](file:///Users/bittu/Desktop/projects/group-reco/reco_new-method/group-reco/tests/test_weighting.py)
- Unit tests for rarity weights.
#### [NEW] [tests/test_greedy.py](file:///Users/bittu/Desktop/projects/group-reco/reco_new-method/group-reco/tests/test_greedy.py)
- Unit tests for optimization logic and diminishing returns.
#### [NEW] [tests/test_end_to_end.py](file:///Users/bittu/Desktop/projects/group-reco/reco_new-method/group-reco/tests/test_end_to_end.py)
- Integration test running the full pipeline on sample data.

## Verification Plan

### Automated Tests
- Run `pytest -q` to execute all unit and end-to-end tests.
- Verify `03_tests.md` is generated and contains pass documentation.

### Manual Verification
- Run the CLI command:
  ```bash
  python -m groupreco.cli run --data data/sample
  ```
- Verify the generation of:
  - `reports/01_data_summary.md`: Check for correct rarity lists.
  - `reports/02_run_report.md`: Check that teams are formed and coverage is reported.
