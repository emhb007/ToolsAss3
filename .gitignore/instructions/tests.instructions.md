---
applyTo: "**/tests.py,**/test_*.py,**/tests/**/*.py"
---

# Testing Standards

## Purpose
How tests should be structured and what they must cover, so Copilot-written
tests are actually useful rather than superficial "does it run" checks.

## Framework and structure
- Use `pytest` with `pytest-django`, not `unittest.TestCase`, for new tests
  unless a file already uses `TestCase` — stay consistent within a file.
- Structure each test using **Arrange / Act / Assert**, with a blank line
  between each section for readability.
- One behaviour per test. If a test needs "and" to describe what it checks,
  split it.
- Name tests descriptively:
  `test_<unit>_<scenario>_<expected_outcome>`, e.g.
  `test_trip_clean_deadline_after_trip_date_raises_validation_error`.

## What must be covered
For every model, form, and view added or changed, include tests for:
- The "happy path" (valid input succeeds and produces the expected state).
- At least one validation/failure case (invalid input is rejected with a
  clear error, not a silent pass or an unhandled exception).
- Edge cases called out in the spec — e.g. a permission deadline that has
  already passed, a trip with zero students, a slip marked returned without
  consent.
- Permission/auth boundaries — a logged-out or unauthorised user cannot
  reach a view that should be restricted.

## Test data
- Use `factory_boy` factories (or Django's `TestCase.setUp`) to build test
  data rather than duplicating object-creation boilerplate in every test.
- Never use real student names, phone numbers, or medical data in tests or
  fixtures — use obviously fake values.
- Keep tests independent — no test should depend on another test's side
  effects or on execution order.

## Assertions
- Assert on specific values/messages, not just "no exception was raised".
  For validation tests, assert the `ValidationError` mentions the expected
  field or message.
- For views, assert both the HTTP status code and the relevant content/state
  change (e.g. object was actually created, correct template was used).

## Coverage expectation
- New models, forms, and business-logic methods (e.g.
  `Trip.total_expected_income`) should have test coverage before being
  considered done — don't leave calculation or validation logic untested.
- Coverage is a signal, not a target to game: a file at 100% with only
  happy-path tests is worse than one at 80% with meaningful edge-case tests.
