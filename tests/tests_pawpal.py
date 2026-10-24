from pawpal_system import Pet, Priority, Task


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
