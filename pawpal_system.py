from dataclasses import dataclass, field, fields, replace
from datetime import date, datetime, time, timedelta
from enum import Enum
from itertools import combinations
from typing import List, Optional

DEFAULT_DAY_START = time(8, 0)
# Days until the next occurrence of a recurring task; any other frequency is a one-off.
RECURRENCE_DAYS = {"daily": 1, "weekly": 7}


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Task:
    title: str
    category: str
    duration_minutes: int
    priority: Priority
    frequency: str = "once"
    preferred_time: Optional[time] = None
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def update(self, **changes) -> None:
        """Update the given task fields by name, raising AttributeError for unknown fields."""
        valid = {f.name for f in fields(self)}
        for key, value in changes.items():
            if key not in valid:
                raise AttributeError(f"Task has no field '{key}'")
            setattr(self, key, value)

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task completed; for daily/weekly tasks return a new copy due on the next occurrence."""
        self.completed = True
        step = RECURRENCE_DAYS.get(self.frequency)
        if step is None:
            return None
        return replace(self, completed=False, due_date=date.today() + timedelta(days=step))


@dataclass
class Pet:
    name: str
    breed: str
    weight: float
    age: int
    tasks: List[Task] = field(default_factory=list)

    def update_info(self, **changes) -> None:
        """Update the given pet fields by name, raising AttributeError for unknown fields."""
        valid = {f.name for f in fields(self)} - {"tasks"}
        for key, value in changes.items():
            if key not in valid:
                raise AttributeError(f"Pet has no field '{key}'")
            setattr(self, key, value)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list if it is present."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_tasks_for_day(self, day: date) -> List[Task]:
        """Return this pet's incomplete tasks that are due on or before the given day."""
        return [t for t in self.tasks if not t.completed and t.due_date <= day]


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: dict = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pets."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's pets if it is present."""
        if pet in self.pets:
            self.pets.remove(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


@dataclass
class ScheduledItem:
    task: Task
    pet: Pet
    start_time: time
    end_time: time
    reason: str = ""


@dataclass
class DailyPlan:
    day: date
    items: List[ScheduledItem] = field(default_factory=list)
    total_minutes: int = 0
    skipped_tasks: List[Task] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_item(self, item: ScheduledItem) -> None:
        """Add a scheduled item and include its duration in the plan total."""
        self.items.append(item)
        self.total_minutes += item.task.duration_minutes

    def explain(self) -> str:
        """Return a readable summary of the plan, including any skipped tasks."""
        lines = [f"Plan for {self.day.isoformat()} ({self.total_minutes} min total):"]
        for item in self.items:
            lines.append(
                f"  {item.start_time:%H:%M}-{item.end_time:%H:%M} "
                f"{item.task.title} ({item.pet.name}) - {item.reason}"
            )
        if self.skipped_tasks:
            lines.append("Skipped (not enough time):")
            for task in self.skipped_tasks:
                lines.append(f"  {task.title} ({task.duration_minutes} min, {task.priority.name})")
        for warning in self.warnings:
            lines.append(f"WARNING: {warning}")
        return "\n".join(lines)


def _add_minutes(start: time, minutes: int) -> Optional[time]:
    """Return start + minutes, or None if it passes midnight."""
    end = datetime.combine(date.min, start) + timedelta(minutes=minutes)
    if end.date() != date.min:
        return None
    return end.time()


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def generate_plan(self, day: date) -> DailyPlan:
        """Build a time-ordered plan for the day from all of the owner's pets' tasks."""
        plan = DailyPlan(day=day, warnings=self.find_time_conflicts(day))
        pet_of = {}
        tasks = []
        for pet in self.owner.pets:
            for task in pet.get_tasks_for_day(day):
                pet_of[id(task)] = pet
                tasks.append(task)

        ordered = self.sort_tasks(tasks)
        kept = self.filter_by_constraints(ordered, self.owner.available_minutes)
        kept_ids = {id(t) for t in kept}
        plan.skipped_tasks = [t for t in ordered if id(t) not in kept_ids]

        # Place tasks in time order; a preferred time is honoured when it's still free.
        kept = self.sort_by_time(kept)
        cursor = self.owner.preferences.get("day_start", DEFAULT_DAY_START)
        for task in kept:
            start = cursor
            if task.preferred_time is not None and task.preferred_time > cursor:
                start = task.preferred_time
            end = _add_minutes(start, task.duration_minutes)
            if end is None:
                plan.skipped_tasks.append(task)
                continue
            item = ScheduledItem(task=task, pet=pet_of[id(task)], start_time=start, end_time=end)
            item.reason = self.explain_choice(item)
            plan.add_item(item)
            cursor = end
        return plan

    def sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority (high first), then preferred time, then shortest duration."""
        return sorted(
            tasks,
            key=lambda t: (
                -t.priority.value,
                t.preferred_time is None,
                t.preferred_time or time.min,
                t.duration_minutes,
            ),
        )

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by preferred time of day, earliest first, with untimed tasks last."""
        return sorted(tasks, key=lambda t: (t.preferred_time is None, t.preferred_time or time.min))

    def filter_tasks(self, pet_name: Optional[str] = None, completed: Optional[bool] = None) -> List[Task]:
        """Return the owner's tasks, optionally limited to one pet (by name) and/or completion status."""
        return [
            task
            for pet in self.owner.pets
            if pet_name is None or pet.name.lower() == pet_name.lower()
            for task in pet.tasks
            if completed is None or task.completed == completed
        ]

    def mark_task_complete(self, pet: Pet, task: Task) -> Optional[Task]:
        """Complete a task and, if it recurs, add its next occurrence to the pet; return that new task."""
        next_task = task.mark_complete()
        if next_task is not None:
            pet.add_task(next_task)
        return next_task

    def find_time_conflicts(self, day: date) -> List[str]:
        """Return warning messages for tasks (any pets) whose preferred-time windows overlap."""
        timed = [
            (pet, task)
            for pet in self.owner.pets
            for task in pet.get_tasks_for_day(day)
            if task.preferred_time is not None
        ]
        timed.sort(key=lambda pair: pair[1].preferred_time)
        warnings = []
        for (pet_a, a), (pet_b, b) in combinations(timed, 2):
            end_a = _add_minutes(a.preferred_time, a.duration_minutes) or time.max
            if b.preferred_time < end_a:  # sorted by start, so b starts at or after a
                warnings.append(
                    f"'{a.title}' ({pet_a.name}, {a.preferred_time:%H:%M}-{end_a:%H:%M}) "
                    f"overlaps '{b.title}' ({pet_b.name}, starts {b.preferred_time:%H:%M})"
                )
        return warnings

    def filter_by_constraints(self, tasks: List[Task], available_minutes: int) -> List[Task]:
        """Greedily keep tasks, in the given order, that still fit in the time budget."""
        kept, used = [], 0
        for task in tasks:
            if used + task.duration_minutes <= available_minutes:
                kept.append(task)
                used += task.duration_minutes
        return kept

    def detect_conflicts(self, items: List[ScheduledItem]) -> List[ScheduledItem]:
        """Return the items that overlap an earlier item by start time."""
        conflicts = []
        latest_end = None
        for item in sorted(items, key=lambda i: i.start_time):
            if latest_end is not None and item.start_time < latest_end:
                conflicts.append(item)
            if latest_end is None or item.end_time > latest_end:
                latest_end = item.end_time
        return conflicts

    def explain_choice(self, item: ScheduledItem) -> str:
        """Return a short reason describing why a task was placed where it was."""
        task = item.task
        reason = f"{task.priority.name.lower()} priority"
        if task.preferred_time is not None:
            if item.start_time == task.preferred_time:
                reason += f", scheduled at its preferred time {task.preferred_time:%H:%M}"
            else:
                reason += f", preferred {task.preferred_time:%H:%M} but placed after earlier tasks"
        reason += f", {task.duration_minutes} min"
        return reason
