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

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
==================================================
Today's Schedule for Jordan (Saturday, October 24, 2026)
==================================================
Plan for 2026-10-24 (110 min total):
  08:00-08:30 Morning walk (Biscuit) - high priority, scheduled at its preferred time 08:00, 30 min
  09:00-09:10 Feeding (Biscuit) - high priority, scheduled at its preferred time 09:00, 10 min
  12:30-12:35 Medication (Luna) - high priority, scheduled at its preferred time 12:30, 5 min
  17:00-17:45 Grooming (Biscuit) - low priority, scheduled at its preferred time 17:00, 45 min
  18:30-18:50 Play session (Luna) - medium priority, scheduled at its preferred time 18:30, 20 min
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
