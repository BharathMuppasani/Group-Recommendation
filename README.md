# Group Recommendation System

This project implements a Group Recommendation System that optimally forms teams for research proposals based on skill rarity and diminishing returns.

## Usage

### Prerequisites
- Python 3.10+
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
  *(Note: Requires `rich`, `scikit-learn` for metrics if needed, `nltk` for NLP)*

### Running the Analysis
Run the main script to process all datasets in `data/raw` and generate results in `results/`:

```bash
python run.py
```

**Options:**
- `--data <path>`: Specify input data directory (default: `data/raw`)
- `--results <path>`: Specify output directory (default: `results`)

## Results Summary

The system processes multiple datasets ("Sets"). Below is the average performance summary for the current datasets:

| Dataset | Avg Coverage | Avg Goodness Score | Avg Seat Cost | Proposals Processed |
|---|---|---|---|---|
| Set 1   | 84.60%       | 0.4253             | 4.3152        | 100                 |
| Set 2   | 90.96%       | 0.4320             | 4.1105        | 434                 |
| Set 3   | 90.96%       | 0.4320             | 4.1105        | 434                 |
| Set 4   | 100.00%      | 0.4529             | 2.2632        | 500                 |

**Key Metrics:**
- **Coverage**: Percentage of required proposal skills covered by the selected team.
- **Goodness Score**: A composite metric (0-1) evaluating team quality using `M1` metric (requires `nlp_techniques.py` and `metrics_scorer.py`).
- **Seat Cost**: The "cost" of the team based on skill rarity weighting.
