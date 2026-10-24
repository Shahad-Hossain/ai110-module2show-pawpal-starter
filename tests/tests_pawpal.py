from datetime import date, time, timedelta

import pytest

from pawpal_system import Owner, Pet, Priority, Scheduler, Task


def make_owner():
    owner = Owner(name="Jordan", available_minutes=180)
    biscuit = Pet(name="Biscuit", breed="Lab", weight=60.0, age=3)
    luna = Pet(name="Luna", breed="Tabby", weight=9.0, age=2)
    owner.add_pet(biscuit)
    owner.add_pet(luna)
    return owner, biscuit, luna


def test_mark_complete_changes_status():
    task = Task("Morning walk", "exercise", 30, Priority.HIGH)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", breed="Golden Retriever", weight=65.0, age=4)
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feeding", "food", 10, Priority.HIGH))
    assert len(pet.tasks) == 1

    pet.add_task(Task("Grooming", "care", 45, Priority.LOW))
    assert len(pet.tasks) == 2


def test_sort_by_time_orders_earliest_first_and_untimed_last():
    owner, biscuit, _ = make_owner()
    late = Task("Late", "x", 5, Priority.LOW, preferred_time=time(18, 0))
    untimed = Task("Untimed", "x", 5, Priority.LOW)
    early = Task("Early", "x", 5, Priority.LOW, preferred_time=time(7, 30))

    result = Scheduler(owner).sort_by_time([late, untimed, early])

    assert [t.title for t in result] == ["Early", "Late", "Untimed"]


def test_filter_tasks_by_pet_and_status():
    owner, biscuit, luna = make_owner()
    walk = Task("Walk", "x", 10, Priority.HIGH)
    play = Task("Play", "x", 10, Priority.LOW)
    biscuit.add_task(walk)
    luna.add_task(play)
    walk.mark_complete()
    scheduler = Scheduler(owner)

    assert scheduler.filter_tasks(pet_name="luna") == [play]
    assert scheduler.filter_tasks(completed=True) == [walk]
    assert scheduler.filter_tasks(pet_name="Biscuit", completed=False) == []


@pytest.mark.parametrize("frequency, days", [("daily", 1), ("weekly", 7)])
def test_recurring_task_creates_next_occurrence(frequency, days):
    owner, biscuit, _ = make_owner()
    task = Task("Walk", "x", 30, Priority.HIGH, frequency=frequency)
    biscuit.add_task(task)

    next_task = Scheduler(owner).mark_task_complete(biscuit, task)

    assert task.completed is True
    assert next_task.completed is False
    assert next_task.due_date == date.today() + timedelta(days=days)
    assert next_task in biscuit.tasks


def test_one_off_task_does_not_recur():
    owner, biscuit, _ = make_owner()
    task = Task("Vet", "x", 30, Priority.HIGH)
    biscuit.add_task(task)

    assert Scheduler(owner).mark_task_complete(biscuit, task) is None
    assert len(biscuit.tasks) == 1


def test_future_task_is_not_scheduled_today():
    owner, biscuit, _ = make_owner()
    biscuit.add_task(Task("Later", "x", 10, Priority.HIGH, due_date=date.today() + timedelta(days=1)))

    plan = Scheduler(owner).generate_plan(date.today())

    assert plan.items == []


def test_overlapping_tasks_across_pets_produce_warning():
    owner, biscuit, luna = make_owner()
    biscuit.add_task(Task("Walk", "x", 30, Priority.HIGH, preferred_time=time(8, 0)))
    luna.add_task(Task("Vet call", "x", 15, Priority.HIGH, preferred_time=time(8, 15)))

    warnings = Scheduler(owner).find_time_conflicts(date.today())

    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Vet call" in warnings[0]


def test_back_to_back_tasks_do_not_conflict():
    owner, biscuit, luna = make_owner()
    biscuit.add_task(Task("Walk", "x", 30, Priority.HIGH, preferred_time=time(8, 0)))
    luna.add_task(Task("Feed", "x", 10, Priority.HIGH, preferred_time=time(8, 30)))

    assert Scheduler(owner).find_time_conflicts(date.today()) == []
