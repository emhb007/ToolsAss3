# Contributing

## Before opening a pull request
Run these locally — CI will fail the build if any of them fail:

```bash
black --check .
isort --check-only .
ruff check .
pytest
```

To auto-fix formatting/import order:

```bash
black .
isort .
```

## Coding standards
This repo uses GitHub Copilot custom instructions to keep AI-assisted code
consistent with our standards. If you're using Copilot, it will pick these
up automatically:

- `.github/copilot-instructions.md` — repo-wide context and principles
- `.github/instructions/python.instructions.md` — PEP 8, typing, linting
- `.github/instructions/django.instructions.md` — Django app conventions
- `.github/instructions/tests.instructions.md` — test structure and coverage

These files are also the standard for human-written code — if Copilot
wouldn't be allowed to skip a rule, neither should a manual PR.

## Data handling
This app stores personal data about minors (names, emergency contacts,
medical needs). Do not commit real student data in any form — fixtures,
screenshots, or example output. Use obviously fake data for testing and
demos.
