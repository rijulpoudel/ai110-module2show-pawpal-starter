# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output from running `python main.py`:

```
Today's Schedule (sorted by time)
  08:00 — Morning walk (Mochi, 30 min, priority: high, pending)
  08:00 — Feeding (Mochi, 10 min, priority: high, pending)
  08:30 — Feeding (Biscuit, 10 min, priority: high, pending)
  09:00 — Litter box cleaning (Biscuit, 5 min, priority: medium, pending)
  18:00 — Evening walk (Mochi, 30 min, priority: high, pending)

Conflict warnings:
  ⚠️  Conflict at 08:00: 'Morning walk' (Mochi) overlaps with 'Feeding' (Mochi)

Completing task: Morning walk for Mochi
  Recurrence created: Morning walk at 08:00

Mochi's Tasks
  08:00 — Morning walk (Mochi, 30 min, priority: high, done)
  08:00 — Feeding (Mochi, 10 min, priority: high, pending)
  18:00 — Evening walk (Mochi, 30 min, priority: high, pending)
  08:00 — Morning walk (Mochi, 30 min, priority: high, pending)

All Pending Tasks
  08:00 — Feeding (Mochi, 10 min, priority: high, pending)
  08:30 — Feeding (Biscuit, 10 min, priority: high, pending)
  09:00 — Litter box cleaning (Biscuit, 5 min, priority: medium, pending)
  18:00 — Evening walk (Mochi, 30 min, priority: high, pending)
  08:00 — Morning walk (Mochi, 30 min, priority: high, pending)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Tests cover task completion, task counting, chronological sorting, daily recurrence,
one-off (non-recurring) tasks, same-time conflict detection, and filtering by pet/completion status.

Sample test output:

```
collected 7 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [ 14%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [ 28%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 42%]
tests/test_pawpal.py::test_daily_recurrence_creates_task_for_next_day PASSED [ 57%]
tests/test_pawpal.py::test_once_task_does_not_recur PASSED               [ 71%]
tests/test_pawpal.py::test_detect_conflicts_flags_same_date_and_time PASSED [ 85%]
tests/test_pawpal.py::test_filter_tasks_by_pet_and_completion PASSED     [100%]

============================== 7 passed in 0.01s ===============================
```

**Confidence Level:** ⭐⭐⭐⭐☆ (4/5) — see reflection.md section 4b for what's still untested.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts by `(due_date, time)` tuple, so recurring tasks pushed to a future date sort after today's tasks even at the same clock time. |
| Filtering | `Scheduler.filter_tasks()` | Filters by `pet_name` and/or `completed` status; used to build per-pet views and "pending only" views. |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags tasks sharing the same `(due_date, time)` key with a warning string; does not block scheduling, just surfaces the warning. |
| Recurring tasks | `Task.mark_complete()` / `Task._next_occurrence()` | Daily tasks get a due date `+1 day`, weekly tasks `+7 days`; `Scheduler.complete_task()` re-attaches the new task to the same pet. |

## 📸 Demo Walkthrough

1. Enter the owner's name and add one or more pets (name + species) under "Owner & Pet".
2. Under "Tasks", pick a pet, enter a task title, time (HH:MM), duration, priority, and frequency (once/daily/weekly), then click "Add task". Repeat to build up a few tasks, including two at the same time for the same pet.
3. Click "Generate schedule" to see today's pending tasks in chronological order in a table.
4. If two tasks share the same time, a `⚠️` conflict warning appears above the table naming both tasks.
5. Click "Mark done" next to any task to complete it — if it's a daily/weekly task, PawPal+ automatically schedules its next occurrence, which you'll see on the next "Generate schedule" for the following day.

**Screenshot or video** *(optional)*: not included — the CLI output above and the walkthrough steps demonstrate the working behavior.
