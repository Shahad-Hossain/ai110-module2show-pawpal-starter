from datetime import date, time

from pawpal_system import Owner, Pet, Priority, Scheduler, Task


def show(title: str, tasks) -> None:
    print(f"\n{title}")
    for t in tasks:
        when = f"{t.preferred_time:%H:%M}" if t.preferred_time else "--:--"
        status = "done" if t.completed else "todo"
        print(f"  {when}  {t.title:<14} [{t.frequency}, due {t.due_date}, {status}]")


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=180)
    biscuit = Pet(name="Biscuit", breed="Golden Retriever", weight=65.0, age=4)
    luna = Pet(name="Luna", breed="Tabby Cat", weight=9.5, age=2)
    owner.add_pet(biscuit)
    owner.add_pet(luna)

    # Added deliberately out of time order.
    biscuit.add_task(Task("Grooming", "care", 45, Priority.LOW, preferred_time=time(17, 0)))
    luna.add_task(Task("Play session", "enrichment", 20, Priority.MEDIUM, preferred_time=time(18, 30)))
    biscuit.add_task(Task("Morning walk", "exercise", 30, Priority.HIGH, frequency="daily", preferred_time=time(8, 0)))
    luna.add_task(Task("Medication", "health", 5, Priority.HIGH, frequency="weekly", preferred_time=time(12, 30)))
    biscuit.add_task(Task("Feeding", "food", 10, Priority.HIGH, frequency="daily", preferred_time=time(9, 0)))
    luna.add_task(Task("Vet call", "health", 15, Priority.MEDIUM, preferred_time=time(8, 15)))  # overlaps the walk

    scheduler = Scheduler(owner)

    # --- Sorting and filtering ---
    show("All tasks, as added:", scheduler.filter_tasks())
    show("Sorted by time:", scheduler.sort_by_time(scheduler.filter_tasks()))
    show("Luna's tasks only:", scheduler.filter_tasks(pet_name="Luna"))

    # --- Recurring tasks ---
    walk = biscuit.tasks[1]
    next_walk = scheduler.mark_task_complete(biscuit, walk)
    print(f"\nCompleted '{walk.title}' (daily) -> next one due {next_walk.due_date}")
    show("Completed tasks:", scheduler.filter_tasks(completed=True))
    show("Still to do (includes the new recurring copy):", scheduler.filter_tasks(completed=False))

    # --- Conflict detection and today's schedule ---
    print("\n" + "=" * 60)
    print(f"Today's Schedule for {owner.name} ({date.today():%A, %B %d, %Y})")
    print("=" * 60)
    print(scheduler.generate_plan(date.today()).explain())


if __name__ == "__main__":
    main()
