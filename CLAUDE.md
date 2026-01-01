# CLAUDE.md

## Architecture
Read ARCHITECTURE.md for an overview.

## Coding Rules
Read CODING.md for an overview.

Additionally:
- Prefer small diffs; no unrequested refactors.
- Add or update tests for changed logic.
- Always ask before adding third party dependencies.

## Definition of Done
- Tests passing.
- Linter passing.
- Coverage is same or better.

## Communication
- Be brief in all interactions. 
- Don't use unnecessary courtesies. 

## Commits
- Never start a plan on a dirty repo. Changes must be committed first.

## Commands

```bash
# Activate venv and install
source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest -v

# Run linter
ruff check .

# Run coverage
coverage run -m pytest
coverage report
```

## Common mistakes
- Test data should be generated, _not_ literals.
- Don't write old school code, i.e. use `Path` instead of `str`.
- Don't add separate tests for checking type annotations.
- Don't use Java-style getters. Use property annotations instead.
