from datetime import date, time

from pawpal_system import Owner, Pet, Priority, Scheduler, Task


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=120)

    biscuit = Pet(name="Biscuit", breed="Golden Retriever", weight=65.0, age=4)
    luna = Pet(name="Luna", breed="Tabby Cat", weight=9.5, age=2)
    owner.add_pet(biscuit)
    owner.add_pet(luna)

    biscuit.add_task(Task("Morning walk", "exercise", 30, Priority.HIGH, preferred_time=time(8, 0)))
    biscuit.add_task(Task("Feeding", "food", 10, Priority.HIGH, preferred_time=time(9, 0)))
    biscuit.add_task(Task("Grooming", "care", 45, Priority.LOW, preferred_time=time(17, 0)))
    luna.add_task(Task("Medication", "health", 5, Priority.HIGH, preferred_time=time(12, 30)))
    luna.add_task(Task("Play session", "enrichment", 20, Priority.MEDIUM, preferred_time=time(18, 30)))

    plan = Scheduler(owner).generate_plan(date.today())

    print("=" * 50)
    print(f"Today's Schedule for {owner.name} ({plan.day:%A, %B %d, %Y})")
    print("=" * 50)
    print(plan.explain())


if __name__ == "__main__":
    main()
