"""Core logic layer for PawPal+: Task, Pet, Owner, and Scheduler classes."""

from dataclasses import dataclass, field
from datetime import date

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
        pass


@dataclass
class Pet:
    """A pet belonging to an owner, along with its care tasks."""

    name: str
    species: str
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task):
        """Attach a task to this pet."""
        pass

    def task_count(self) -> int:
        """Return how many tasks this pet currently has."""
        pass


@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    pets: list = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Register a new pet under this owner."""
        pass

    def get_pet(self, name: str):
        """Look up one of this owner's pets by name."""
        pass

    def all_tasks(self) -> list:
        """Flatten every task across all of this owner's pets."""
        pass


@dataclass
class Scheduler:
    """Organizes an owner's tasks into a schedule: sorting, filtering, conflicts, recurrence."""

    owner: Owner

    def sort_by_time(self, tasks: list) -> list:
        """Return tasks ordered chronologically."""
        pass

    def filter_tasks(self, tasks: list, pet_name: str = None, completed: bool = None) -> list:
        """Return the subset of tasks matching the given filters."""
        pass

    def detect_conflicts(self, tasks: list) -> list:
        """Return warning strings for tasks scheduled at the same date and time."""
        pass

    def build_daily_plan(self) -> list:
        """Return today's incomplete tasks, sorted by time."""
        pass

    def complete_task(self, task: Task):
        """Mark a task complete and handle recurrence."""
        pass
