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

## Branching Strategy & Solo Developer Workflow

**Branch Protection on `main`:**
- Require passing status checks (CI: Ruff, tests, notebook checks) before merge.
- Require branches to be up-to-date with `main` (strict checks enabled).
- No manual PR review requirement (since you can't approve your own PR as a solo developer).
- Squash merge preferred to keep history clean.

**Solo Developer Workflow:**
1. Create a feature branch from `main`.
2. Make changes, commit, and push to remote.
3. Open a PR from your branch to `main`.
4. CI pipeline runs automatically; if all checks pass, you can squash and merge the PR.
5. `main` is automatically protected—CI must pass before merge is allowed.

**View/Update Branch Protection:**
To view or modify branch protection rules in GitHub:
1. Go to repo **Settings** → **Branches** → **Branch protection rules** → **Edit** (main).
2. Current settings: CI status checks required, no manual review needed, auto-dismiss stale reviews.