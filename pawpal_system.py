from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum
from typing import List, Optional


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
    frequency: str = "daily"
    preferred_time: Optional[time] = None
    completed: bool = False

    def update(self, **fields) -> None:
        pass

    def mark_complete(self) -> None:
        pass


@dataclass
class Pet:
    name: str
    breed: str
    weight: float
    age: int
    tasks: List[Task] = field(default_factory=list)

    def update_info(self, **fields) -> None:
        pass

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def get_tasks_for_day(self, day: date) -> List[Task]:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: dict = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass

    def get_all_tasks(self) -> List[Task]:
        pass


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

    def add_item(self, item: ScheduledItem) -> None:
        pass

    def explain(self) -> str:
        pass


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def generate_plan(self, day: date) -> DailyPlan:
        pass

    def sort_tasks(self, tasks: List[Task]) -> List[Task]:
        pass

    def filter_by_constraints(self, tasks: List[Task], available_minutes: int) -> List[Task]:
        pass

    def detect_conflicts(self, items: List[ScheduledItem]) -> List[ScheduledItem]:
        pass

    def explain_choice(self, item: ScheduledItem) -> str:
        pass
