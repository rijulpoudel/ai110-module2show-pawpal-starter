"""Core logic layer for PawPal+: Task, Pet, Owner, and Scheduler classes."""

from dataclasses import dataclass, field
from datetime import date, timedelta

VALID_PRIORITIES = ("low", "medium", "high")
VALID_FREQUENCIES = ("once", "daily", "weekly")


@dataclass
class Task:
    """A single pet care activity (e.g. walk, feeding, medication)."""

    title: str
    time: str  # "HH:MM" 24-hour format
    duration_minutes: int
    priority: str = "medium"
    frequency: str = "once"
    pet_name: str = ""
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def mark_complete(self):
        """Mark this task done; return the next occurrence if it recurs, else None."""
        self.completed = True
        if self.frequency == "once":
            return None
        return self._next_occurrence()

    def _next_occurrence(self):
        """Build the follow-up Task for daily/weekly recurring tasks."""
        delta_days = 1 if self.frequency == "daily" else 7
        return Task(
            title=self.title,
            time=self.time,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            pet_name=self.pet_name,
            completed=False,
            due_date=self.due_date + timedelta(days=delta_days),
        )


@dataclass
class Pet:
    """A pet belonging to an owner, along with its care tasks."""

    name: str
    species: str
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task):
        """Attach a task to this pet, tagging it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def task_count(self) -> int:
        """Return how many tasks this pet currently has."""
        return len(self.tasks)


@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    pets: list = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Register a new pet under this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str):
        """Look up one of this owner's pets by name."""
        for pet in self.pets:
            if pet.name == name:
                return pet
        return None

    def all_tasks(self) -> list:
        """Flatten every task across all of this owner's pets."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks


@dataclass
class Scheduler:
    """Organizes an owner's tasks into a schedule: sorting, filtering, conflicts, recurrence."""

    owner: Owner

    def sort_by_time(self, tasks: list) -> list:
        """Return tasks ordered chronologically by date, then by HH:MM time."""
        return sorted(tasks, key=lambda t: (t.due_date, t.time))

    def filter_tasks(self, tasks: list, pet_name: str = None, completed: bool = None) -> list:
        """Return the subset of tasks matching the given pet name and/or completion status."""
        result = tasks
        if pet_name is not None:
            result = [t for t in result if t.pet_name == pet_name]
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        return result

    def detect_conflicts(self, tasks: list) -> list:
        """Return warning strings for any tasks scheduled at the same date and time."""
        warnings = []
        seen = {}
        for task in tasks:
            key = (task.due_date, task.time)
            if key in seen:
                other = seen[key]
                warnings.append(
                    f"Conflict at {task.time}: '{other.title}' ({other.pet_name}) "
                    f"overlaps with '{task.title}' ({task.pet_name})"
                )
            else:
                seen[key] = task
        return warnings

    def build_daily_plan(self) -> list:
        """Return today's incomplete tasks across all pets, sorted by time."""
        today = date.today()
        tasks = self.filter_tasks(self.owner.all_tasks(), completed=False)
        tasks = [t for t in tasks if t.due_date == today]
        return self.sort_by_time(tasks)

    def complete_task(self, task: Task):
        """Mark a task complete and schedule its next occurrence if it recurs."""
        next_task = task.mark_complete()
        if next_task is not None:
            pet = self.owner.get_pet(task.pet_name)
            if pet is not None:
                pet.add_task(next_task)
        return next_task
