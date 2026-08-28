---
applyTo: "trips/**/*.py"
---

# Django App Standards — `trips`

## Purpose
Conventions specific to this Django app, so models, views, and forms stay
consistent with the rest of the project and with Django best practice.

## Models
- Put validation that depends on more than one field in the model's
  `clean()` method, not in a view or a form's `clean()` alone — forms should
  call `full_clean()`/`is_valid()` so model-level rules are always enforced,
  even from the admin or a management command.
- Every model needs a `__str__` method that returns something useful in the
  admin and shell.
- Use `related_name` on ForeignKey/ManyToMany fields when a model has more
  than one relation to the same target, or when the default reverse name
  would be ambiguous.
- Add `Meta.ordering` where a sensible default order exists (e.g. trips by
  `trip_date`).
- New fields that affect existing tables require a migration — don't leave
  `makemigrations` unrun or assume it happened.

## Views
- Prefer class-based views (`ListView`, `DetailView`, `CreateView`, etc.)
  over function-based views unless the logic is a one-off action (e.g. a
  toggle endpoint) that doesn't fit the CBV pattern well.
- Any view that creates, edits, or deletes data must be behind
  `LoginRequiredMixin` at minimum; use `PermissionRequiredMixin` or
  `UserPassesTestMixin` where the app-level permission scheme requires it.
- Use `get_object_or_404` rather than raw `.get()` lookups in views.
- Avoid business logic in templates — compute values (counts, percentages,
  overdue flags) in the view or as model properties/methods.

## Querysets
- Use `select_related`/`prefetch_related` when a view or template will
  access related objects in a loop, to avoid N+1 queries — this matters on
  the trip report and respondent list views in particular.
- Don't write raw SQL unless the ORM genuinely can't express the query;
  if you do, parameterise it and say why in a comment.

## Forms
- Use `ModelForm` wherever a form maps directly to a model; only use a
  plain `Form` for input that doesn't correspond to a single model instance
  (e.g. the bulk student-paste form).
- Surface validation errors to the user via form errors, not via silent
  failures or generic 500s.

## Data sensitivity
- Fields such as `medical_needs` and `emergency_contact_number` should
  never appear in log statements, `print()` debugging, or error messages
  sent to Sentry/console in a way that leaks the value itself.
- Don't add real student data to fixtures or test data — use clearly fake
  names (e.g. "Test Student") and fake but validly-formatted phone numbers.
