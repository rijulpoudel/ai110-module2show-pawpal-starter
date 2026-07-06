"""CLI demo: verifies the PawPal+ backend logic before wiring it into the UI."""

from pawpal_system import Owner, Pet, Task, Scheduler


def print_schedule(title, tasks):
    print(f"\n{title}")
    if not tasks:
        print("  (no tasks)")
        return
    for task in tasks:
        status = "done" if task.completed else "pending"
        print(
            f"  {task.time} — {task.title} ({task.pet_name}, {task.duration_minutes} min, "
            f"priority: {task.priority}, {status})"
        )


def main():
    owner = Owner(name="Jordan")

    mochi = Pet(name="Mochi", species="dog")
    biscuit = Pet(name="Biscuit", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(biscuit)

    mochi.add_task(Task(title="Morning walk", time="08:00", duration_minutes=30, priority="high", frequency="daily"))
    mochi.add_task(Task(title="Evening walk", time="18:00", duration_minutes=30, priority="high", frequency="daily"))
    mochi.add_task(Task(title="Feeding", time="08:00", duration_minutes=10, priority="high", frequency="daily"))
    biscuit.add_task(Task(title="Feeding", time="08:30", duration_minutes=10, priority="high", frequency="daily"))
    biscuit.add_task(Task(title="Litter box cleaning", time="09:00", duration_minutes=5, priority="medium", frequency="weekly"))

    scheduler = Scheduler(owner=owner)

    plan = scheduler.build_daily_plan()
    print_schedule("Today's Schedule (sorted by time)", plan)

    conflicts = scheduler.detect_conflicts(plan)
    if conflicts:
        print("\nConflict warnings:")
        for warning in conflicts:
            print(f"  ⚠️  {warning}")

    walk = mochi.tasks[0]
    print(f"\nCompleting task: {walk.title} for {walk.pet_name}")
    next_walk = scheduler.complete_task(walk)
    if next_walk:
        print(f"  Recurrence created: {next_walk.title} at {next_walk.time}")

    dog_tasks = scheduler.filter_tasks(owner.all_tasks(), pet_name="Mochi")
    print_schedule("Mochi's Tasks", scheduler.sort_by_time(dog_tasks))

    pending_tasks = scheduler.filter_tasks(owner.all_tasks(), completed=False)
    print_schedule("All Pending Tasks", scheduler.sort_by_time(pending_tasks))


if __name__ == "__main__":
    main()
