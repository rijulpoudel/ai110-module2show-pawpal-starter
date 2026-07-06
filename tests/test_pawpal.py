"""Automated tests for the PawPal+ backend (pawpal_system.py)."""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler


def make_scheduler():
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    owner.add_pet(mochi)
    return owner, mochi, Scheduler(owner=owner)


def test_mark_complete_changes_status():
    task = Task(title="Walk", time="08:00", duration_minutes=20, frequency="once")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog")
    assert pet.task_count() == 0
    pet.add_task(Task(title="Feeding", time="08:00", duration_minutes=10))
    assert pet.task_count() == 1


def test_sort_by_time_returns_chronological_order():
    owner, mochi, scheduler = make_scheduler()
    mochi.add_task(Task(title="Evening walk", time="18:00", duration_minutes=30))
    mochi.add_task(Task(title="Morning walk", time="08:00", duration_minutes=30))
    mochi.add_task(Task(title="Feeding", time="12:00", duration_minutes=10))

    ordered = scheduler.sort_by_time(mochi.tasks)
    assert [t.title for t in ordered] == ["Morning walk", "Feeding", "Evening walk"]


def test_daily_recurrence_creates_task_for_next_day():
    owner, mochi, scheduler = make_scheduler()
    task = Task(title="Morning walk", time="08:00", duration_minutes=30, frequency="daily")
    mochi.add_task(task)

    scheduler.complete_task(task)

    assert task.completed is True
    new_tasks = [t for t in mochi.tasks if t is not task]
    assert len(new_tasks) == 1
    next_task = new_tasks[0]
    assert next_task.completed is False
    assert next_task.due_date == date.today() + timedelta(days=1)


def test_once_task_does_not_recur():
    owner, mochi, scheduler = make_scheduler()
    task = Task(title="Vet appointment", time="10:00", duration_minutes=60, frequency="once")
    mochi.add_task(task)

    scheduler.complete_task(task)

    assert mochi.task_count() == 1


def test_detect_conflicts_flags_same_date_and_time():
    owner, mochi, scheduler = make_scheduler()
    mochi.add_task(Task(title="Morning walk", time="08:00", duration_minutes=30))
    mochi.add_task(Task(title="Feeding", time="08:00", duration_minutes=10))

    conflicts = scheduler.detect_conflicts(mochi.tasks)
    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]


def test_filter_tasks_by_pet_and_completion():
    owner, mochi, scheduler = make_scheduler()
    biscuit = Pet(name="Biscuit", species="cat")
    owner.add_pet(biscuit)
    mochi.add_task(Task(title="Walk", time="08:00", duration_minutes=30))
    biscuit.add_task(Task(title="Feeding", time="09:00", duration_minutes=10, completed=True))

    all_tasks = owner.all_tasks()
    assert len(scheduler.filter_tasks(all_tasks, pet_name="Mochi")) == 1
    assert len(scheduler.filter_tasks(all_tasks, completed=True)) == 1
