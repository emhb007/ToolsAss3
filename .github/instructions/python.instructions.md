---
applyTo: "**/*.py"
---

# Python Code Standards

## Purpose
Style and quality rules for all Python source in this repository, so
generated code is consistent and passes CI linting without manual cleanup.

## Style (PEP 8 + formatting)
- Follow PEP 8. Formatting is enforced by **Black** (line length 88) and
  **isort** for import ordering — write code that would pass both unchanged.
- Use `snake_case` for functions/variables, `PascalCase` for classes,
  `UPPER_SNAKE_CASE` for constants.
- One import per line where practical; group imports stdlib → third-party →
  local, separated by a blank line (isort default).
- No unused imports or variables; no commented-out code left in place.
- Keep functions focused — if a view or method is doing more than one clear
  job, split it.

## Type hints and docstrings
- Add type hints to all function/method signatures, including return types.
- Use `Optional[X]` / `X | None` explicitly rather than leaving a default of
  `None` untyped.
- Write docstrings in **Google style** for any non-trivial function, class,
  or model method — briefly state purpose, args, returns, and raises.

## Linting
- Code must be clean under **ruff** (or flake8 if ruff isn't configured) —
  don't suppress warnings with blanket `# noqa` unless the reason is
  commented.
- No bare `except:` — catch specific exceptions, and never silently swallow
  an exception without at least logging it.
- Use the `logging` module, not `print()`, for anything other than local,
  throwaway debugging that will be removed before commit.

## Naming and clarity
- Prefer descriptive names over abbreviations (`emergency_contact_number`,
  not `ecn`).
- Avoid magic numbers/strings — use named constants or model `choices`
  where a value has meaning (e.g. status codes, deadlines).
