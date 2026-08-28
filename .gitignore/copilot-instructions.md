# Copilot Instructions — Trip Admin (School Trip Permission & Reporting App)

## Project context
This is a Django full-stack app used by school staff to record trips, generate
permission slip PDFs, track returned slips, and report on respondents. It
handles personal data about minors (names, emergency contacts, medical
needs), so correctness and data-handling discipline matter more than speed.

## Stack
- Python 3.11+, Django 5.x
- django-crispy-forms + Bootstrap 5 for templates
- WeasyPrint for PDF generation
- pytest + pytest-django for tests
- Package/dependency management via `requirements.txt` (or `pyproject.toml`
  if the project has migrated — check before adding a new dependency file)

## General principles
- Prefer explicit, readable code over clever one-liners.
- Favour Django's built-in patterns (class-based views, ModelForms, the ORM)
  over hand-rolled alternatives, unless there's a documented reason not to.
- Validation belongs on the model/form (`clean()`), not scattered across
  views or templates.
- Never invent business rules that weren't specified (e.g. don't assume a
  refund policy, a specific ParentPay API, or an authentication scheme
  unless asked) — ask or leave a `# TODO` comment instead of guessing.
- Treat any field holding student names, contact numbers, or medical
  information as sensitive: no logging of these values, no printing to
  console, no committing of real student data as fixtures.

## More specific rules
See the path-specific instruction files in `.github/instructions/` for:
- `python.instructions.md` — PEP 8, typing, formatting/linting for all `.py` files
- `django.instructions.md` — Django-specific conventions for the `trips` app
- `tests.instructions.md` — test structure and coverage expectations

## Before proposing a change
- Check whether an existing model, form, or view already covers the need
  before creating a new one.
- If a change touches `models.py`, mention that a migration
  (`python manage.py makemigrations`) is required — don't silently skip it.
- Flag (in a code comment, not silently) any place where you're uncertain
  whether a requirement was fully specified.
