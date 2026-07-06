# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The core actions a user needs are: (1) add a pet under an owner, (2) add a care task (with a time,
duration, priority, and frequency) to a pet, and (3) generate a daily schedule that shows which
tasks are due today, in order.

That mapped to four classes:

- **Task** — a single care activity: `title`, `time` ("HH:MM"), `duration_minutes`, `priority`,
  `frequency` (once/daily/weekly), `pet_name`, `completed`, `due_date`. Owns `mark_complete()`,
  which is also where recurrence is decided.
- **Pet** — `name`, `species`, and a list of `Task`s. Owns `add_task()` and `task_count()`.
- **Owner** — `name` and a list of `Pet`s. Owns `add_pet()`, `get_pet()`, and `all_tasks()` (a flat
  view across all pets, since the scheduler shouldn't have to know how pets store their tasks).
- **Scheduler** — holds a reference to an `Owner` and is the only class with algorithmic logic:
  `sort_by_time()`, `filter_tasks()`, `detect_conflicts()`, `build_daily_plan()`, and
  `complete_task()`.

Task/Pet/Owner are intentionally "dumb" dataclasses that just hold state and simple accessors; all
the decision-making (sorting, filtering, conflicts) lives in Scheduler. That split made it much
easier to unit test the algorithms without needing a full UI or session state.

**b. Design changes**

Yes — the original `Task` only had a `time` string (no date), because I initially thought "today's
plan" only needed a clock time. That broke as soon as I implemented recurrence: advancing a daily
task by `timedelta(days=1)` and reformatting it back to `"HH:MM"` produced the *exact same string*,
since a bare time has no concept of which day it's on. A "completed" daily task would immediately
look identical to a "new" one. I added a `due_date` field to `Task`, changed `sort_by_time()` and
`detect_conflicts()` to key off `(due_date, time)` instead of `time` alone, and made
`build_daily_plan()` filter to `due_date == date.today()`. This is the kind of bug that's invisible
until you actually run the recurrence path end-to-end in `main.py` — the class skeleton looked fine
on paper.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers: **time** (tasks are shown in chronological order so an owner can follow
along through the day), **completion status** (only pending tasks show up in the daily plan —
finished tasks don't clutter it), **pet** (tasks can be filtered per pet), and **frequency**
(recurring tasks regenerate themselves instead of disappearing after one use). Time ordering
mattered most because the primary use case is "what do I do next, in what order" — priority and
duration are shown as metadata on each task but don't currently reorder the list, since a pet
owner going through their day cares more about *when* something happens than an abstract priority
score.

**b. Tradeoffs**

`detect_conflicts()` only flags tasks with an **exact matching `(due_date, time)`** — it does not
check for overlapping time *ranges* using `duration_minutes`. A 30-minute walk at 08:00 and a
10-minute feeding at 08:15 would actually overlap in real life, but my scheduler won't flag that.
I chose exact-match because it's simple, predictable, and cheap (a single pass with a dict lookup),
and for a first version it still catches the most common real mistake — literally double-booking a
time slot. Interval-overlap conflict detection is a reasonable next step, but it adds complexity
(sorting by start time, tracking end times, handling multi-pet overlap rules) that didn't feel
justified before the simpler version was proven out and tested.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude in agent mode for most of this build: describing the four entities and constraints
in plain language and asking it to translate that into a Mermaid UML diagram, then into Python
dataclass skeletons, then into full implementations of the Scheduler's algorithmic methods
(sorting, filtering, conflict detection, recurrence). The most useful prompts were narrow and
gave it a concrete artifact to react to — e.g. "here's my Task/Pet/Owner skeleton, how should
Scheduler retrieve all tasks across an Owner's pets?" — rather than open-ended "design a pet
scheduler" prompts, which tend to produce generic, over-engineered answers.

**b. Judgment and verification**

The first version of recurring tasks (described in 1b) was AI-generated and looked correct: it
took `self.time`, parsed it with `datetime.strptime`, added a `timedelta`, and reformatted it. I
didn't accept it as final because running it through `main.py` (the CLI-first workflow) made the
bug immediately visible — the "next" walk printed at the identical time as the "current" one, with
no way to tell them apart. I verified this wasn't just a display issue by inspecting the actual
`Task` objects in a debug print, confirmed the underlying date info was simply never captured, and
fixed it by adding a `due_date` field rather than trying to encode the date inside the time string.
The lesson: an AI suggestion that type-checks and runs without error can still be silently wrong
about the actual domain model — running the real CLI demo end-to-end caught what a pure code review
would not have.

---

## 4. Testing and Verification

**a. What you tested**

`tests/test_pawpal.py` covers: marking a task complete flips its status; adding a task increases a
pet's task count; `sort_by_time()` returns tasks in chronological order; completing a daily task
creates a new task due exactly one day later; a `"once"` task does *not* regenerate after
completion; two tasks at the same date/time are flagged as a conflict; and `filter_tasks()`
correctly narrows by pet name and by completion status. These map directly to the riskiest logic
in the app — recurrence and conflict detection are the two places where a subtle date/time bug
(like the one in 1b) could silently corrupt a schedule without throwing an error.

**b. Confidence**

I'm fairly confident (4/5) in the tested paths — all 7 tests pass, and I also verified behavior
manually by running `main.py` and clicking through the Streamlit UI (adding pets/tasks, generating
a schedule, marking a recurring task complete, confirming a conflict warning appears). What I
haven't tested and would prioritize next: weekly recurrence specifically (only daily is covered),
behavior when a task's `time` string is malformed (no validation currently exists on `Task.time`
or `priority`/`frequency` values — the `VALID_PRIORITIES`/`VALID_FREQUENCIES` tuples exist but
aren't enforced), and what happens when `detect_conflicts()` or `build_daily_plan()` run against an
owner with zero pets or zero tasks (should return an empty list — currently untested).

---

## 5. Reflection

**a. What went well**

The CLI-first workflow (build and verify `pawpal_system.py` through `main.py` before touching
Streamlit) paid off directly — it's what surfaced the recurrence bug in a debuggable text output
instead of buried inside session-state UI behavior, and it meant the Streamlit wiring in `app.py`
was just plumbing by the time I got to it, not debugging.

**b. What you would improve**

I'd implement interval-based conflict detection (using `duration_minutes` to catch true overlaps,
not just exact time matches) and add input validation on `Task` so an invalid `priority` or
malformed `time` string fails fast with a clear error instead of silently sorting incorrectly.

**c. Key takeaway**

Being the "lead architect" with an AI assistant means the AI is very good at producing code that
matches the shape of what you asked for, but it doesn't know your domain assumptions unless you've
made them explicit and then verified them by actually running the thing — the recurrence bug in 1b
existed because both the AI and I initially treated "time" as sufficient without a date, and no
amount of re-reading the code caught it; only executing the real recurrence path did.
