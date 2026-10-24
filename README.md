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

## ✨ Features

- **Multiple pets, one owner:** track any number of pets, each with their own list of care tasks (duration, priority, category, repeat frequency, optional preferred time).
- **Sorting by time:** tasks are ordered by preferred time, earliest first, with untimed tasks last (`Scheduler.sort_by_time`).
- **Priority-based planning:** when time is short, tasks are ranked by priority (high first), then preferred time, then shortest duration (`Scheduler.sort_tasks`).
- **Time-budget fitting:** a greedy pass keeps the tasks that fit in the owner's available minutes, and the rest are listed as skipped (`Scheduler.filter_by_constraints`).
- **Filtering:** view tasks by pet (case-insensitive) and/or by done vs. to-do (`Scheduler.filter_tasks`).
- **Conflict warnings:** if two tasks' time windows overlap (same time, or one starts before another ends), even across different pets, the planner shows a warning instead of crashing (`Scheduler.find_time_conflicts`).
- **Daily and weekly recurrence:** completing a daily or weekly task automatically creates the next one, due the next day or next week (`Task.mark_complete`, `Scheduler.mark_task_complete`).
- **Explained schedule:** every scheduled task gets a reason (priority, whether it got its preferred time or was pushed back), and tasks that would run past midnight are skipped.
- **Streamlit UI:** add pets and tasks, filter and sort the task list, complete tasks, and generate the day's plan with warnings, metrics, and a schedule table.

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

## 🧪 Testing PawPal+

To run the tests:

```bash
python -m pytest
```

My tests are in `tests/tests_pawpal.py` and cover the main scheduling behaviors:

- **Sorting:** tasks come back in chronological order (earliest preferred time first, untimed tasks last), and the generated plan has ascending start times.
- **Recurrence:** completing a daily or weekly task adds a new copy due the next day or next week. One-off tasks don't repeat.
- **Conflict detection:** the `Scheduler` warns when tasks overlap or share the same time, even across different pets. Back-to-back tasks are not flagged.
- **Basics:** marking a task complete, adding tasks to a pet, filtering by pet name and status, and keeping future tasks out of today's plan.

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\Sabbirus\ai110-module2show-pawpal-starter
configfile: pytest.ini
testpaths: tests
collected 38 items

tests\tests_pawpal.py ......................................             [100%]

============================= 38 passed in 0.10s ==============================
```

**Confidence Level: ★★★★★ (5/5)**

All 38 tests pass. Edge cases covered: empty owners and pets, a zero or exactly-filled time budget, long tasks that can't block shorter ones, ties in sorting, untimed tasks, preferred times that are free versus taken, tasks that run to or past midnight, completed, overdue, and future tasks, weekly and unknown recurrence frequencies (including overdue tasks), overlapping, contained, duplicate, and back-to-back time windows, invalid field updates, and removing items that don't exist.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sorting by time | `Scheduler.sort_by_time()` | Orders tasks by `preferred_time`, earliest first; tasks with no preferred time go last. |
| Sorting by importance | `Scheduler.sort_tasks()` | Priority (high first), then preferred time, then shortest duration. Used to decide what survives when time is short. |
| Filtering by pet / status | `Scheduler.filter_tasks(pet_name, completed)` | Both filters are optional and can be combined; pet names are case-insensitive. |
| Filtering by time budget | `Scheduler.filter_by_constraints()` | Greedily keeps tasks (in priority order) that fit in the owner's available minutes; the rest are listed as skipped. |
| Conflict detection | `Scheduler.find_time_conflicts()` | Compares the preferred-time windows (start to start + duration) of all pets' tasks and returns warning strings instead of raising. Back-to-back tasks are not conflicts. Warnings appear in `DailyPlan.warnings` and in the app. |
| Recurring tasks | `Task.mark_complete()`, `Scheduler.mark_task_complete()` | Completing a `daily` or `weekly` task creates a new copy due `today + 1 day` or `today + 7 days` (via `timedelta`). Tasks only appear in a day's plan once `due_date` has arrived. |
| Daily plan | `Scheduler.generate_plan()` | Combines the above: sorts, fits to the time budget, places timed tasks at their preferred time when free, and records a reason for every item. |

## 📸 Demo Walkthrough

**What you can do in the app** (`streamlit run app.py`):

- Set the owner's name and how many minutes they have today.
- Add pets (name, breed, weight, age).
- Add tasks for a pet with a duration, priority, repeat (once, daily, weekly), and an optional preferred time.
- Filter the task list by pet or status. It is always sorted by preferred time.
- Mark a task complete. Daily and weekly tasks come back automatically.
- Generate today's schedule and read why each task was placed where it was.

**Example workflow:**

1. Add a pet, for example Biscuit the Golden Retriever.
2. Schedule a task, like "Morning walk" (30 min, high priority, daily, 08:00), then add a second one at the same time.
3. The task list shows a conflict warning with the two tasks that clash and how to fix it.
4. Click **Generate schedule** to see today's plan: tasks in time order, minutes used out of minutes available, and a warning for anything skipped.
5. Mark the walk complete and a new "Morning walk" appears, due tomorrow.

**Scheduler behaviors shown:** sorting by time, filtering by pet and status, daily and weekly recurrence, time-budget fitting, and preferred-time placement with a reason for each task. Conflict warnings appear in the Streamlit app (see step 3). The CLI demo below completes the conflicting morning walk before building the plan, so its schedule has no warnings.

**Sample CLI output** (`python main.py`):

```
All tasks, as added:
  17:00  Grooming       [once, due 2026-10-24, todo]
  08:00  Morning walk   [daily, due 2026-10-24, todo]
  09:00  Feeding        [daily, due 2026-10-24, todo]
  18:30  Play session   [once, due 2026-10-24, todo]
  12:30  Medication     [weekly, due 2026-10-24, todo]
  08:15  Vet call       [once, due 2026-10-24, todo]

Sorted by time:
  08:00  Morning walk   [daily, due 2026-10-24, todo]
  08:15  Vet call       [once, due 2026-10-24, todo]
  09:00  Feeding        [daily, due 2026-10-24, todo]
  12:30  Medication     [weekly, due 2026-10-24, todo]
  17:00  Grooming       [once, due 2026-10-24, todo]
  18:30  Play session   [once, due 2026-10-24, todo]

Luna's tasks only:
  18:30  Play session   [once, due 2026-10-24, todo]
  12:30  Medication     [weekly, due 2026-10-24, todo]
  08:15  Vet call       [once, due 2026-10-24, todo]

Completed 'Morning walk' (daily) -> next one due 2026-10-25

Completed tasks:
  08:00  Morning walk   [daily, due 2026-10-24, done]

Still to do (includes the new recurring copy):
  17:00  Grooming       [once, due 2026-10-24, todo]
  09:00  Feeding        [daily, due 2026-10-24, todo]
  08:00  Morning walk   [daily, due 2026-10-25, todo]
  18:30  Play session   [once, due 2026-10-24, todo]
  12:30  Medication     [weekly, due 2026-10-24, todo]
  08:15  Vet call       [once, due 2026-10-24, todo]

============================================================
Today's Schedule for Jordan (Saturday, October 24, 2026)
============================================================
Plan for 2026-10-24 (95 min total):
  08:15-08:30 Vet call (Luna) - medium priority, scheduled at its preferred time 08:15, 15 min
  09:00-09:10 Feeding (Biscuit) - high priority, scheduled at its preferred time 09:00, 10 min
  12:30-12:35 Medication (Luna) - high priority, scheduled at its preferred time 12:30, 5 min
  17:00-17:45 Grooming (Biscuit) - low priority, scheduled at its preferred time 17:00, 45 min
  18:30-18:50 Play session (Luna) - medium priority, scheduled at its preferred time 18:30, 20 min
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
