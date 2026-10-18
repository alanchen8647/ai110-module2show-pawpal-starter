import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import STATUS_COMPLETE, STATUS_PENDING, Pet, Task


def test_mark_task_complete_changes_status():
    task = Task()
    assert task.status == STATUS_PENDING

    task.markTaskComplete()

    assert task.status == STATUS_COMPLETE


def test_adding_task_increases_pet_task_count():
    pet = Pet()
    before = len(pet.tasks)

    task = Task()
    task.setTimeStart(9, 0)
    task.setDuration(0, 30)
    pet.addTask(task)

    assert len(pet.tasks) == before + 1
    assert task.petId == pet.petId
