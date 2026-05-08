# Balatro — ML Exploration Scaffold

This repository is scaffolded for exploratory machine-learning work while keeping code modular and testable.

## Installation

Recommended (editable install):

```bash
# Create and activate a virtualenv
python -m venv .venv
# Windows
.venv\Scripts\activate
# Unix
source .venv/bin/activate

pip install -r requirements.txt
pip install -r dev-requirements.txt
pip install -e .
```

## Project Structure

- notebooks/ — ordered experiment notebooks (prefix with numbers to control order)
- src/balatro/ — project package (local importable package; modular monolith)
- data/
  - raw/ — original data (ignored by git)
  - interim/
  - processed/
- models/ — serialized model artifacts (ignored by git)
- scripts/ — small scripts (e.g., notebook checks)
- tests/ — unit and integration tests

## How to Run Experiments

- Use the notebooks in `notebooks/` for exploratory work. Keep outputs stripped before committing.
- To run CI checks locally:

```bash
ruff format --check .
python scripts/check_notebooks_stripped.py
pytest -q
```

Use `nbstripout` or `jupyter nbconvert --clear-output` to remove outputs before committing.

## Branching Strategy

- Protect `main`: require passing CI checks and at least one approving review before merge.
- Prefer `squash` merges to keep history concise.
- Use short-lived feature/topic branches branching from `main`.