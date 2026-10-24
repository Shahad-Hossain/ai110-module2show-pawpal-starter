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


# --- Core behavior checks ---


def test_sorting_returns_tasks_in_chronological_order():
    owner, biscuit, luna = make_owner()
    biscuit.add_task(Task("Evening walk", "x", 20, Priority.LOW, preferred_time=time(18, 0)))
    luna.add_task(Task("Breakfast", "x", 10, Priority.LOW, preferred_time=time(7, 30)))
    biscuit.add_task(Task("Lunch", "x", 10, Priority.LOW, preferred_time=time(12, 0)))
    scheduler = Scheduler(owner)

    ordered = scheduler.sort_by_time(owner.get_all_tasks())
    plan = scheduler.generate_plan(date.today())

    assert [t.preferred_time for t in ordered] == [time(7, 30), time(12, 0), time(18, 0)]
    starts = [item.start_time for item in plan.items]
    assert starts == sorted(starts)
    assert [item.task.title for item in plan.items] == ["Breakfast", "Lunch", "Evening walk"]


def test_completing_daily_task_creates_task_for_following_day():
    owner, biscuit, _ = make_owner()
    task = Task("Feeding", "food", 10, Priority.HIGH, frequency="daily")
    biscuit.add_task(task)

    next_task = Scheduler(owner).mark_task_complete(biscuit, task)

    assert task.completed is True
    assert next_task is not task
    assert next_task.title == "Feeding"
    assert next_task.completed is False
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert len(biscuit.tasks) == 2


def test_scheduler_flags_duplicate_times():
    owner, biscuit, luna = make_owner()
    biscuit.add_task(Task("Walk", "x", 30, Priority.HIGH, preferred_time=time(9, 0)))
    luna.add_task(Task("Feed", "x", 10, Priority.HIGH, preferred_time=time(9, 0)))

    warnings = Scheduler(owner).find_time_conflicts(date.today())
    plan = Scheduler(owner).generate_plan(date.today())

    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Feed" in warnings[0]
    assert plan.warnings == warnings


# --- Edge cases ---

from pawpal_system import DailyPlan, ScheduledItem  # noqa: E402


def test_empty_owner_and_petless_tasks_produce_empty_plan():
    plan = Scheduler(Owner(name="Empty", available_minutes=60)).generate_plan(date.today())
    assert plan.items == [] and plan.skipped_tasks == [] and plan.warnings == []
    assert plan.total_minutes == 0

    owner, _, _ = make_owner()
    assert Scheduler(owner).generate_plan(date.today()).items == []


def test_budget_exactly_filled_keeps_task_and_zero_budget_skips_all():
    owner, biscuit, _ = make_owner()
    owner.available_minutes = 30
    biscuit.add_task(Task("Walk", "x", 30, Priority.HIGH))
    plan = Scheduler(owner).generate_plan(date.today())
    assert [i.task.title for i in plan.items] == ["Walk"] and plan.total_minutes == 30

    owner.available_minutes = 0
    plan = Scheduler(owner).generate_plan(date.today())
    assert plan.items == [] and [t.title for t in plan.skipped_tasks] == ["Walk"]


def test_long_high_priority_task_does_not_block_shorter_ones_that_fit():
    owner, biscuit, _ = make_owner()
    owner.available_minutes = 60
    biscuit.add_task(Task("Big", "x", 50, Priority.HIGH))
    biscuit.add_task(Task("Too big", "x", 40, Priority.MEDIUM))
    biscuit.add_task(Task("Small", "x", 10, Priority.LOW))
    plan = Scheduler(owner).generate_plan(date.today())
    assert {i.task.title for i in plan.items} == {"Big", "Small"}
    assert [t.title for t in plan.skipped_tasks] == ["Too big"]


def test_sort_tasks_priority_then_time_then_duration():
    owner, _, _ = make_owner()
    low = Task("low", "x", 5, Priority.LOW, preferred_time=time(6, 0))
    high_untimed = Task("high untimed", "x", 5, Priority.HIGH)
    high_late = Task("high late", "x", 5, Priority.HIGH, preferred_time=time(15, 0))
    high_early_long = Task("high early long", "x", 30, Priority.HIGH, preferred_time=time(9, 0))
    high_early_short = Task("high early short", "x", 10, Priority.HIGH, preferred_time=time(9, 0))
    result = Scheduler(owner).sort_tasks([low, high_untimed, high_late, high_early_long, high_early_short])
    assert [t.title for t in result] == [
        "high early short", "high early long", "high late", "high untimed", "low",
    ]


def test_sorting_empty_and_single_lists():
    scheduler = Scheduler(make_owner()[0])
    assert scheduler.sort_by_time([]) == [] and scheduler.sort_tasks([]) == []
    task = Task("Solo", "x", 5, Priority.LOW)
    assert scheduler.sort_by_time([task]) == [task]


def test_tasks_are_placed_back_to_back_from_default_day_start():
    owner, biscuit, _ = make_owner()
    biscuit.add_task(Task("A", "x", 30, Priority.HIGH))
    biscuit.add_task(Task("B", "x", 15, Priority.MEDIUM))
    items = Scheduler(owner).generate_plan(date.today()).items
    assert (items[0].start_time, items[0].end_time) == (time(8, 0), time(8, 30))
    assert (items[1].start_time, items[1].end_time) == (time(8, 30), time(8, 45))


def test_custom_day_start_preference_is_used():
    owner, biscuit, _ = make_owner()
    owner.preferences["day_start"] = time(6, 30)
    biscuit.add_task(Task("A", "x", 10, Priority.HIGH))
    assert Scheduler(owner).generate_plan(date.today()).items[0].start_time == time(6, 30)


def test_preferred_time_is_honoured_when_free_and_pushed_when_taken():
    owner, biscuit, luna = make_owner()
    biscuit.add_task(Task("Walk", "x", 60, Priority.HIGH, preferred_time=time(9, 0)))
    luna.add_task(Task("Feed", "x", 10, Priority.HIGH, preferred_time=time(9, 30)))
    items = Scheduler(owner).generate_plan(date.today()).items
    assert items[0].start_time == time(9, 0) and "preferred time 09:00" in items[0].reason
    assert items[1].start_time == time(10, 0) and "placed after earlier tasks" in items[1].reason


def test_task_running_past_midnight_is_skipped_not_wrapped():
    owner, biscuit, _ = make_owner()
    biscuit.add_task(Task("Late", "x", 30, Priority.HIGH, preferred_time=time(23, 50)))
    plan = Scheduler(owner).generate_plan(date.today())
    assert plan.items == [] and [t.title for t in plan.skipped_tasks] == ["Late"]
    assert plan.total_minutes == 0


def test_task_ending_exactly_at_midnight_is_skipped():
    owner, biscuit, _ = make_owner()
    biscuit.add_task(Task("Edge", "x", 10, Priority.HIGH, preferred_time=time(23, 50)))
    assert Scheduler(owner).generate_plan(date.today()).items == []


def test_completed_overdue_and_future_tasks_for_a_day():
    pet = Pet("P", "b", 1.0, 1)
    today = date.today()
    done = Task("done", "x", 5, Priority.LOW)
    done.completed = True
    overdue = Task("overdue", "x", 5, Priority.LOW, due_date=today - timedelta(days=3))
    due_today = Task("today", "x", 5, Priority.LOW)
    future = Task("future", "x", 5, Priority.LOW, due_date=today + timedelta(days=1))
    for t in (done, overdue, due_today, future):
        pet.add_task(t)
    assert pet.get_tasks_for_day(today) == [overdue, due_today]


def test_weekly_recurrence_and_unknown_frequency():
    pet = Pet("P", "b", 1.0, 1)
    weekly = Task("w", "x", 5, Priority.LOW, frequency="weekly")
    pet.add_task(weekly)
    nxt = Scheduler(Owner("o", 10, pets=[pet])).mark_task_complete(pet, weekly)
    assert nxt.due_date == date.today() + timedelta(days=7)

    odd = Task("odd", "x", 5, Priority.LOW, frequency="monthly")
    assert odd.mark_complete() is None


def test_recurring_copy_is_independent_and_keeps_fields():
    task = Task("Meds", "health", 5, Priority.HIGH, frequency="daily", preferred_time=time(9, 0))
    nxt = task.mark_complete()
    assert nxt is not task and task.completed and not nxt.completed
    assert (nxt.title, nxt.category, nxt.duration_minutes, nxt.priority, nxt.preferred_time) == (
        "Meds", "health", 5, Priority.HIGH, time(9, 0))
    nxt.update(title="Changed")
    assert task.title == "Meds"


def test_next_occurrence_is_not_scheduled_until_due():
    owner, biscuit, _ = make_owner()
    task = Task("Feed", "x", 10, Priority.HIGH, frequency="daily")
    biscuit.add_task(task)
    scheduler = Scheduler(owner)
    scheduler.mark_task_complete(biscuit, task)
    assert scheduler.generate_plan(date.today()).items == []
    tomorrow = scheduler.generate_plan(date.today() + timedelta(days=1))
    assert [i.task.title for i in tomorrow.items] == ["Feed"]


def test_overdue_recurring_task_next_occurrence_is_from_today():
    task = Task("Feed", "x", 10, Priority.HIGH, frequency="daily", due_date=date.today() - timedelta(days=5))
    assert task.mark_complete().due_date == date.today() + timedelta(days=1)


def test_conflicts_same_pet_contained_and_chained_windows():
    owner, biscuit, _ = make_owner()
    biscuit.add_task(Task("Long", "x", 120, Priority.HIGH, preferred_time=time(9, 0)))
    biscuit.add_task(Task("Inside", "x", 10, Priority.HIGH, preferred_time=time(9, 30)))
    biscuit.add_task(Task("Also inside", "x", 10, Priority.HIGH, preferred_time=time(10, 0)))
    warnings = Scheduler(owner).find_time_conflicts(date.today())
    assert len(warnings) == 2 and all("Long" in w for w in warnings)


def test_conflicts_ignore_untimed_completed_and_other_days():
    owner, biscuit, luna = make_owner()
    biscuit.add_task(Task("Walk", "x", 60, Priority.HIGH, preferred_time=time(9, 0)))
    luna.add_task(Task("Untimed", "x", 60, Priority.HIGH))
    finished = Task("Finished", "x", 60, Priority.HIGH, preferred_time=time(9, 15))
    finished.completed = True
    luna.add_task(finished)
    luna.add_task(Task("Tomorrow", "x", 60, Priority.HIGH, preferred_time=time(9, 15),
                       due_date=date.today() + timedelta(days=1)))
    assert Scheduler(owner).find_time_conflicts(date.today()) == []


def test_conflicts_none_for_empty_owner_and_single_task():
    assert Scheduler(Owner("o", 10)).find_time_conflicts(date.today()) == []
    owner, biscuit, _ = make_owner()
    biscuit.add_task(Task("Walk", "x", 30, Priority.HIGH, preferred_time=time(9, 0)))
    assert Scheduler(owner).find_time_conflicts(date.today()) == []


def test_conflict_near_midnight_does_not_crash():
    owner, biscuit, luna = make_owner()
    biscuit.add_task(Task("Late", "x", 60, Priority.HIGH, preferred_time=time(23, 30)))
    luna.add_task(Task("Later", "x", 5, Priority.HIGH, preferred_time=time(23, 45)))
    assert len(Scheduler(owner).find_time_conflicts(date.today())) == 1


def test_detect_conflicts_overlap_containment_and_back_to_back():
    owner, biscuit, _ = make_owner()
    t = Task("t", "x", 5, Priority.LOW)

    def item(s, e):
        return ScheduledItem(t, biscuit, s, e)

    scheduler = Scheduler(owner)
    assert scheduler.detect_conflicts([]) == []
    assert scheduler.detect_conflicts([item(time(8), time(9)), item(time(9), time(10))]) == []
    overlap = item(time(8, 30), time(9, 30))
    assert scheduler.detect_conflicts([item(time(8), time(9)), overlap]) == [overlap]
    inner_a, inner_b = item(time(9), time(9, 10)), item(time(9, 20), time(9, 30))
    big = item(time(8, 55), time(11))
    assert scheduler.detect_conflicts([inner_b, big, inner_a]) == [inner_a, inner_b]


def test_filter_tasks_unknown_pet_and_no_filters():
    owner, biscuit, luna = make_owner()
    a, b = Task("a", "x", 5, Priority.LOW), Task("b", "x", 5, Priority.LOW)
    biscuit.add_task(a)
    luna.add_task(b)
    scheduler = Scheduler(owner)
    assert scheduler.filter_tasks(pet_name="Nobody") == []
    assert scheduler.filter_tasks() == [a, b]


def test_update_methods_validate_field_names():
    task = Task("t", "x", 5, Priority.LOW)
    task.update(title="new", duration_minutes=20)
    assert (task.title, task.duration_minutes) == ("new", 20)
    with pytest.raises(AttributeError):
        task.update(colour="red")

    pet = Pet("P", "b", 1.0, 1)
    pet.update_info(name="Q", age=2)
    assert (pet.name, pet.age) == ("Q", 2)
    with pytest.raises(AttributeError):
        pet.update_info(tasks=[])
    with pytest.raises(AttributeError):
        pet.update_info(color="red")


def test_removing_missing_task_or_pet_is_a_noop():
    owner, biscuit, luna = make_owner()
    task = Task("t", "x", 5, Priority.LOW)
    biscuit.add_task(task)
    biscuit.remove_task(Task("other", "x", 5, Priority.LOW))
    assert biscuit.tasks == [task]
    biscuit.remove_task(task)
    assert biscuit.tasks == []

    owner.remove_pet(Pet("Ghost", "b", 1.0, 1))
    assert owner.pets == [biscuit, luna]
    owner.remove_pet(luna)
    assert owner.pets == [biscuit]


def test_get_all_tasks_spans_pets_and_plan_explain_lists_skips_and_warnings():
    owner, biscuit, luna = make_owner()
    owner.available_minutes = 30
    biscuit.add_task(Task("Walk", "x", 30, Priority.HIGH, preferred_time=time(9, 0)))
    luna.add_task(Task("Play", "x", 30, Priority.LOW, preferred_time=time(9, 0)))
    assert len(owner.get_all_tasks()) == 2
    text = Scheduler(owner).generate_plan(date.today()).explain()
    assert "Walk (Biscuit)" in text and "Skipped" in text and "Play" in text and "WARNING" in text


def test_dailyplan_add_item_accumulates_total_minutes():
    pet = Pet("P", "b", 1.0, 1)
    plan = DailyPlan(day=date.today())
    for mins in (10, 25):
        task = Task("t", "x", mins, Priority.LOW)
        plan.add_item(ScheduledItem(task, pet, time(8), time(9)))
    assert plan.total_minutes == 35
