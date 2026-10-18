import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import datetime as dt

import pytest

from pawpal_system import PLAN_COMPLETE, STATUS_COMPLETE, STATUS_PENDING, PlanSchedule, Pet, Task


def make_task(start, duration, priority=3, task_type="walk", pet_id=1):
    task = Task()
    task.setType(task_type)
    task.setTimeStart(*start)
    task.setDuration(*duration)
    task.setPriority(priority)
    task.setPet(pet_id)
    return task


def test_untimed_task_is_rejected():
    plan = PlanSchedule()
    task = Task()
    task.setType("walk")
    task.setPriority(3)
    with pytest.raises(ValueError):
        plan.addTasks(task)
    assert plan.arrayOfTasks == []


def test_plan_stays_sorted_by_start_on_insert():
    plan = PlanSchedule()
    plan.addTasks(make_task((18, 0), (0, 20), task_type="grooming", pet_id=2))
    plan.addTasks(make_task((7, 30), (0, 30)))
    plan.addTasks(make_task((12, 0), (0, 5), task_type="medication", pet_id=2))
    starts = [t.startMinutes() for t in plan.arrayOfTasks]
    assert starts == sorted(starts)


def test_sort_by_time_orders_by_hour_then_minutes():
    plan = PlanSchedule()
    late = make_task((18, 5), (0, 20), pet_id=1)
    early = make_task((7, 30), (0, 30), pet_id=2)
    mid = make_task((12, 0), (0, 5), pet_id=3)
    plan.addTasks(late)
    plan.addTasks(early)
    plan.addTasks(mid)
    plan.arrayOfTasks.reverse()
    plan.sort_by_time()
    assert plan.arrayOfTasks == [early, mid, late]


def test_filter_tasks_by_status_and_pet_name():
    rex = Pet()
    rex.setName("Rex")
    rex.petId = 1
    miso = Pet()
    miso.setName("Miso")
    miso.petId = 2
    plan = PlanSchedule()
    walk = make_task((7, 30), (0, 30), pet_id=1)
    meds = make_task((12, 0), (0, 5), task_type="medication", pet_id=2)
    feed = make_task((18, 0), (0, 15), task_type="feeding", pet_id=1)
    for t in (walk, meds, feed):
        plan.addTasks(t)
    meds.markTaskComplete()

    assert plan.filter_tasks(status=STATUS_COMPLETE) == [meds]
    assert plan.filter_tasks(status=STATUS_PENDING) == [walk, feed]
    assert plan.filter_tasks(pet_name="  rex ", pets=[rex, miso]) == [walk, feed]
    assert plan.filter_tasks(
        status=STATUS_PENDING, pet_name="Rex", pets=[rex, miso]
    ) == [walk, feed]
    assert plan.filter_tasks(pet_name="Nobody", pets=[rex, miso]) == []
    assert plan.filter_tasks() == [walk, meds, feed]
    with pytest.raises(ValueError):
        plan.filter_tasks(status="done")


def test_daily_task_completion_creates_next_day_instance():
    walk = make_task((7, 30), (0, 30), pet_id=1)
    walk.setRecurrence("daily")
    walk.setDueDate(dt.date(2026, 10, 18))

    following = walk.markTaskComplete()

    assert walk.status == STATUS_COMPLETE
    assert following is not None
    assert following.taskId != walk.taskId
    assert following.status == STATUS_PENDING
    assert following.dueDate == dt.date(2026, 10, 19)
    assert following.recurrence == "daily"
    assert following.petId == walk.petId
    assert following.timeWindow() == walk.timeWindow()


def test_weekly_task_completion_creates_instance_seven_days_later():
    bath = make_task((10, 0), (0, 45), task_type="bath", pet_id=1)
    bath.setRecurrence("weekly")
    bath.setDueDate(dt.date(2026, 10, 18))

    assert bath.markTaskComplete().dueDate == dt.date(2026, 10, 25)


def test_recurring_task_without_due_date_is_based_on_today():
    walk = make_task((7, 30), (0, 30), pet_id=1)
    walk.setRecurrence("daily")

    following = walk.markTaskComplete()

    assert following.dueDate == dt.date.today() + dt.timedelta(days=1)


def test_one_off_task_creates_no_next_instance():
    walk = make_task((7, 30), (0, 30), pet_id=1)
    assert walk.markTaskComplete() is None


def test_completing_twice_creates_only_one_next_instance():
    walk = make_task((7, 30), (0, 30), pet_id=1)
    walk.setRecurrence("daily")
    walk.setDueDate(dt.date(2026, 10, 18))

    assert walk.markTaskComplete() is not None
    assert walk.markTaskComplete() is None


def test_invalid_recurrence_is_rejected():
    walk = make_task((7, 30), (0, 30), pet_id=1)
    with pytest.raises(ValueError):
        walk.setRecurrence("monthly")


def test_plan_completion_returns_next_occurrences_for_recurring_tasks():
    plan = PlanSchedule()
    walk = make_task((7, 30), (0, 30), pet_id=1)
    walk.setRecurrence("daily")
    walk.setDueDate(dt.date(2026, 10, 18))
    meds = make_task((12, 0), (0, 5), task_type="medication", pet_id=2)
    plan.addTasks(walk)
    plan.addTasks(meds)

    following = plan.markPlanComplete()

    assert [t.dueDate for t in following] == [dt.date(2026, 10, 19)]
    assert plan.status == PLAN_COMPLETE
    assert all(t.status == STATUS_COMPLETE for t in plan.arrayOfTasks)
    assert len(plan.arrayOfTasks) == 2


def test_find_gap_returns_earliest_fit():
    plan = PlanSchedule()
    plan.addTasks(make_task((9, 0), (1, 0)))    # 09:00-10:00
    plan.addTasks(make_task((10, 30), (0, 30), pet_id=2))  # 10:30-11:00
    # Searching from 09:00: 20 min fits right after the first task at 10:00.
    assert plan.checkForTimeAvailability(0, 20, 9, 0) == (10, 0)
    # 45 min does not fit in the 10:00-10:30 gap, so it lands after 11:00.
    assert plan.checkForTimeAvailability(0, 45, 9, 0) == (11, 0)


def test_find_gap_respects_earliest_and_day_end():
    plan = PlanSchedule()
    assert plan.checkForTimeAvailability(0, 30, 8, 0) == (8, 0)
    assert plan.checkForTimeAvailability(1, 0, 23, 30) is None


def test_higher_priority_task_displaces_overlapping_lower_one():
    plan = PlanSchedule()
    low = make_task((9, 0), (0, 30), priority=2, pet_id=1)
    plan.addTasks(low)
    high = make_task((9, 15), (0, 30), priority=5, pet_id=2)
    displaced = plan.addTasks(high)
    assert displaced == [low]
    assert plan.arrayOfTasks == [high]


def test_lower_priority_task_is_rejected_on_conflict():
    plan = PlanSchedule()
    high = make_task((9, 0), (0, 30), priority=5, pet_id=1)
    plan.addTasks(high)
    low = make_task((9, 15), (0, 30), priority=2, pet_id=2)
    with pytest.raises(ValueError):
        plan.addTasks(low)
    assert plan.arrayOfTasks == [high]


def test_greedy_keeps_higher_priority_tasks_when_a_long_one_is_offered_first():
    plan = PlanSchedule()
    c = make_task((9, 0), (1, 0), priority=3, pet_id=3, task_type="bath")
    a = make_task((9, 0), (0, 30), priority=4, pet_id=1)
    b = make_task((10, 0), (0, 30), priority=4, pet_id=2)
    plan.addTasks(c)
    assert plan.addTasks(a) == [c]
    assert plan.addTasks(b) == []
    # c is bumped by a, and b fits after a, so the plan keeps a and b.
    assert plan.arrayOfTasks == [a, b]


def test_try_add_task_returns_warning_instead_of_raising():
    plan = PlanSchedule()
    high = make_task((9, 0), (0, 30), priority=5, pet_id=1)
    assert plan.tryAddTask(high) == []

    low = make_task((9, 15), (0, 30), priority=2, pet_id=2)
    warnings = plan.tryAddTask(low)
    assert len(warnings) == 1 and warnings[0].startswith("Not scheduled:")
    assert plan.arrayOfTasks == [high]


def test_try_add_task_reports_bumped_tasks():
    plan = PlanSchedule()
    low = make_task((9, 0), (0, 30), priority=2, pet_id=1)
    plan.tryAddTask(low)
    high = make_task((9, 0), (0, 30), priority=5, pet_id=2)
    warnings = plan.tryAddTask(high)
    assert warnings == [f"Bumped by higher priority: walk (task {low.taskId})"]
    assert plan.arrayOfTasks == [high]


def test_removing_a_task_readmits_the_bumped_one():
    plan = PlanSchedule()
    low = make_task((9, 0), (0, 30), priority=2, pet_id=1)
    high = make_task((9, 0), (0, 30), priority=5, pet_id=2)
    plan.addTasks(low)
    plan.addTasks(high)
    plan.removeTasks(high.taskId)
    assert plan.arrayOfTasks == [low]
    with pytest.raises(ValueError):
        plan.removeTasks(high.taskId)


def test_duplicate_task_is_rejected():
    plan = PlanSchedule()
    plan.addTasks(make_task((7, 30), (0, 30), pet_id=1))
    with pytest.raises(ValueError):
        plan.addTasks(make_task((7, 30), (0, 20), pet_id=1))
    # Same time for a different pet is not a duplicate; it conflicts instead.
    with pytest.raises(ValueError):
        plan.addTasks(make_task((7, 30), (0, 20), pet_id=2, priority=1))


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
