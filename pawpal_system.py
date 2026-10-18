"""PawPal+ domain model.

Classes mirror diagrams/uml.mmd. Attributes are dataclass fields.

Link rules:
- PetOwner.pets and Pet.owner are kept in sync. addPet/removePet on the owner
  and removePet on the pet update both sides.
- Removing an owner (removeClient) removes all of its pets.
- Task has no owner field; the owner is reached through Task.petId -> Pet.owner.

Times are stored as hour/minute parts and converted to minutes since midnight
for comparisons. priority is a 1-5 score (5 = most urgent).

IDs are auto-generated from per-kind counters. A later store class should own
these counters so they can be reset in tests and saved with the data.
"""

from __future__ import annotations

import datetime as dt
import itertools
from collections.abc import Iterable
from dataclasses import dataclass, field, replace

MINUTES_PER_DAY = 24 * 60
MIN_PRIORITY = 1
MAX_PRIORITY = 5

STATUS_PENDING = "pending"
STATUS_INCOMPLETE = "incomplete"
STATUS_COMPLETE = "complete"

PLAN_PLANNED = "planned"
PLAN_COMPLETE = "complete"
PLAN_REMOVED = "removed"

RECURRENCE_DAILY = "daily"
RECURRENCE_WEEKLY = "weekly"
_RECURRENCE_DAYS = {RECURRENCE_DAILY: 1, RECURRENCE_WEEKLY: 7}

_id_counters = {
    "client": itertools.count(1),
    "pet": itertools.count(1),
    "task": itertools.count(1),
    "plan": itertools.count(1),
}


def _next_id(kind: str) -> int:
    """Return the next auto-generated ID for `kind` (client, pet, task, plan)."""
    return next(_id_counters[kind])


def _check_text(value: str, label: str) -> str:
    """Return `value` stripped, or raise if it is not a non-empty string."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _check_int(value: int, label: str, low: int, high: int) -> int:
    """Return `value` if it is an int in [low, high], otherwise raise."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")
    if not low <= value <= high:
        raise ValueError(f"{label} must be between {low} and {high}, got {value}")
    return value


def _check_hour_minutes(hour: int, minutes: int, label: str) -> None:
    """Raise if hour is not 0-23 or minutes is not 0-59."""
    _check_int(hour, f"{label} hour", 0, 23)
    _check_int(minutes, f"{label} minutes", 0, 59)


def _duration_minutes(hour: int, minutes: int) -> int:
    """Validate a duration given as hours and minutes and return it in minutes (must be > 0)."""
    _check_hour_minutes(hour, minutes, "duration")
    total = hour * 60 + minutes
    if total == 0:
        raise ValueError("duration must be greater than 0")
    return total


def _overlaps(a: tuple[int, int], b: tuple[int, int]) -> bool:
    """True if the half-open windows (start, end) `a` and `b` share any time."""
    return a[0] < b[1] and b[0] < a[1]


@dataclass
class PetOwner:
    """A pet owner (client) who owns pets."""

    clientId: int = field(default_factory=lambda: _next_id("client"))
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    # Owned pets. Excluded from repr/eq so the Pet <-> PetOwner cycle is safe.
    pets: list[Pet] = field(default_factory=list, repr=False, compare=False)

    def addClient(self, client: PetOwner) -> None:
        """Validate `client` as a PetOwner that is not this owner.

        Registration of clients belongs to a store; the entity itself only
        checks its argument.
        """
        if not isinstance(client, PetOwner):
            raise TypeError("client must be a PetOwner")
        if client is self:
            raise ValueError("an owner cannot be added to itself")

    def setName(self, name: str) -> None:
        """Set the owner's name; raises if it is blank."""
        self.name = _check_text(name, "name")

    def setEmail(self, email: str) -> None:
        """Set the owner's email; raises if it is blank or has no '@'."""
        email = _check_text(email, "email")
        if "@" not in email:
            raise ValueError("email must contain '@'")
        self.email = email

    def setPhone(self, phone: str) -> None:
        """Set the owner's phone number; raises if it is blank."""
        self.phone = _check_text(phone, "phone")

    def removeClient(self, clientId: int) -> None:
        """Remove this owner; every pet in `pets` is removed as well."""
        if clientId != self.clientId:
            raise ValueError(f"client id {clientId} does not match this owner")
        for pet in list(self.pets):
            self.removePet(pet.petId)

    def addPet(self, pet: Pet) -> None:
        """Append `pet` to `pets` and set `pet.owner` / `pet.ownerId` to this owner.

        If the pet belongs to another owner, it is detached from that owner first.
        """
        if not isinstance(pet, Pet):
            raise TypeError("pet must be a Pet")
        if any(p is pet for p in self.pets):
            return
        if pet.owner is not None:
            pet.owner.removePet(pet.petId)
        self.pets.append(pet)
        pet.owner = self
        pet.ownerId = self.clientId

    def removePet(self, petId: int) -> None:
        """Remove the pet from `pets` and clear its `owner` / `ownerId`."""
        for index, pet in enumerate(self.pets):
            if pet.petId == petId:
                del self.pets[index]
                pet.owner = None
                pet.ownerId = None
                return
        raise ValueError(f"pet {petId} is not owned by client {self.clientId}")


@dataclass
class Pet:
    """A pet belonging to a PetOwner."""

    petId: int = field(default_factory=lambda: _next_id("pet"))
    petName: str | None = None
    petSpecies: str | None = None
    breed: str | None = None
    age: int | None = None
    ownerId: int | None = None
    # Back-reference to the owner. Excluded from repr/eq so the cycle is safe.
    owner: PetOwner | None = field(default=None, repr=False, compare=False)
    gender: str | None = None
    animalCategory: str | None = None
    # Tasks for this pet. Excluded from repr/eq to keep comparisons cheap.
    tasks: list[Task] = field(default_factory=list, repr=False, compare=False)

    def createPet(self) -> Pet:
        """Return a new, unowned pet with an auto-generated ID."""
        return Pet()

    def setName(self, name: str) -> None:
        """Set the pet's name; raises if it is blank."""
        self.petName = _check_text(name, "pet name")

    def setSpecies(self, species: str) -> None:
        """Set the pet's species; raises if it is blank."""
        self.petSpecies = _check_text(species, "species")

    def setBreed(self, breed: str) -> None:
        """Set the pet's breed; raises if it is blank."""
        self.breed = _check_text(breed, "breed")

    def setAge(self, age: int) -> None:
        """Set the pet's age in years (0-100)."""
        self.age = _check_int(age, "age", 0, 100)

    def setOwnerId(self, ownerId: int) -> None:
        """Set the owner ID. Changing to a different owner goes through PetOwner.addPet."""
        if self.owner is not None and self.owner.clientId != ownerId:
            raise ValueError("change owner through PetOwner.addPet")
        self.ownerId = ownerId

    def setGender(self, gender: str) -> None:
        """Set the pet's gender; raises if it is blank."""
        self.gender = _check_text(gender, "gender")

    def setAnimalCategory(self, category: str) -> None:
        """Set the pet's animal category; raises if it is blank."""
        self.animalCategory = _check_text(category, "animal category")

    def removePet(self) -> None:
        """Remove this pet from its owner's `pets` list, if it has an owner."""
        if self.owner is None:
            return
        self.owner.removePet(self.petId)

    def addTask(self, task: Task) -> None:
        """Add `task` to this pet and set its `petId` to this pet's ID."""
        if not isinstance(task, Task):
            raise TypeError("task must be a Task")
        if any(t is task for t in self.tasks):
            return
        task.setPet(self.petId)
        self.tasks.append(task)


@dataclass
class Task:
    """A single care task (walk, feeding, meds, grooming, ...) for a pet.

    ownerPreferences is a free-text note from the owner about the task.
    """

    taskId: int = field(default_factory=lambda: _next_id("task"))
    petId: int | None = None
    status: str = STATUS_PENDING
    type: str | None = None
    timeStartHour: int | None = None
    timeStartMinutes: int | None = None
    timeEndHour: int | None = None
    timeEndMinutes: int | None = None
    timeDurationHour: int | None = None
    timeDurationMinutes: int | None = None
    priority: int | None = None
    ownerPreferences: str | None = None
    # None for a one-off task, or RECURRENCE_DAILY / RECURRENCE_WEEKLY.
    recurrence: str | None = None
    # The day this occurrence is due. Unset means today when the next one is computed.
    dueDate: dt.date | None = None
    # Set once this task has spawned its next occurrence. Stops a reopened and
    # re-completed task from spawning a second one.
    _nextSpawned: bool = field(default=False, repr=False, compare=False)

    def createTasks(self) -> Task:
        """Return a new, unscheduled task with an auto-generated ID."""
        return Task()

    def setPet(self, petId: int) -> None:
        """Set the ID of the pet this task belongs to."""
        self.petId = _check_int(petId, "petId", 1, 10**9)

    def setRecurrence(self, recurrence: str | None) -> None:
        """Set how often the task repeats: 'daily', 'weekly', or None for a one-off."""
        if recurrence is not None and recurrence not in _RECURRENCE_DAYS:
            raise ValueError("recurrence must be 'daily', 'weekly', or None")
        self.recurrence = recurrence

    def setDueDate(self, date: dt.date) -> None:
        """Set the day this occurrence is due."""
        if not isinstance(date, dt.date):
            raise TypeError("due date must be a datetime.date")
        self.dueDate = date

    def markTaskComplete(self) -> Task | None:
        """Set the task's status to complete.

        For a daily or weekly task that was not already complete, returns the next
        occurrence as a new pending Task, due 1 or 7 days after this one. Otherwise None.
        """
        was_complete = self.status == STATUS_COMPLETE
        self.status = STATUS_COMPLETE
        if was_complete or self._nextSpawned or self.recurrence is None:
            return None
        base = self.dueDate or dt.date.today()
        following = replace(
            self,
            taskId=_next_id("task"),
            status=STATUS_PENDING,
            dueDate=base + dt.timedelta(days=_RECURRENCE_DAYS[self.recurrence]),
            _nextSpawned=False,
        )
        self._nextSpawned = True
        return following

    def markIncomplete(self) -> None:
        """Set the task's status to incomplete."""
        self.status = STATUS_INCOMPLETE

    def markPending(self) -> None:
        """Set the task's status back to pending."""
        self.status = STATUS_PENDING

    def setType(self, type: str) -> None:
        """Set the task type (e.g. walk, feeding); raises if it is blank."""
        self.type = _check_text(type, "type")

    def setTimeStart(self, hour: int, minutes: int) -> None:
        """Set the start time as hour (0-23) and minutes (0-59)."""
        _check_hour_minutes(hour, minutes, "start")
        self.timeStartHour = hour
        self.timeStartMinutes = minutes

    def setTimeEnd(self, hour: int, minutes: int) -> None:
        """Set the end time as hour (0-23) and minutes (0-59)."""
        _check_hour_minutes(hour, minutes, "end")
        self.timeEndHour = hour
        self.timeEndMinutes = minutes

    def setDuration(self, hour: int, minutes: int) -> None:
        """Set the duration as hours and minutes; the total must be greater than 0."""
        _duration_minutes(hour, minutes)
        self.timeDurationHour = hour
        self.timeDurationMinutes = minutes

    def setPriority(self, priority: int) -> None:
        """Set the 1-5 priority score (5 = most urgent)."""
        self.priority = _check_int(priority, "priority", MIN_PRIORITY, MAX_PRIORITY)

    def setOwnerPreferences(self, preferences: str) -> None:
        """Set the owner's free-text note for this task; raises if it is blank."""
        self.ownerPreferences = _check_text(preferences, "ownerPreferences")

    def startMinutes(self) -> int | None:
        """Start time as minutes since midnight, or None if unset."""
        if self.timeStartHour is None or self.timeStartMinutes is None:
            return None
        return self.timeStartHour * 60 + self.timeStartMinutes

    def endMinutes(self) -> int | None:
        """End time as minutes since midnight.

        Uses the explicit end if set, otherwise start + duration, otherwise None.
        """
        if self.timeEndHour is not None and self.timeEndMinutes is not None:
            return self.timeEndHour * 60 + self.timeEndMinutes
        start = self.startMinutes()
        if start is None or self.timeDurationHour is None or self.timeDurationMinutes is None:
            return None
        return start + self.timeDurationHour * 60 + self.timeDurationMinutes

    def timeWindow(self) -> tuple[int, int] | None:
        """Return (start, end) in minutes, or None if the task is not fully timed."""
        start, end = self.startMinutes(), self.endMinutes()
        if start is None or end is None:
            return None
        if end <= start or end > MINUTES_PER_DAY:
            raise ValueError(f"task {self.taskId} has an invalid time window")
        return start, end


@dataclass
class PlanSchedule:
    """A daily plan: an ordered selection of tasks for one date.

    A plan can span several pets and owners; they are traced via each
    task's petId -> Pet -> owner. Removing a plan does not delete its tasks.
    """

    planId: int = field(default_factory=lambda: _next_id("plan"))
    date: dt.date | None = None
    arrayOfTasks: list[Task] = field(default_factory=list)
    status: str | None = None
    # Every task offered to the plan, keyed by taskId. Tasks bumped by a higher-priority
    # conflict stay here so they return to the plan when the conflict is removed.
    _pool: dict[int, Task] = field(default_factory=dict, repr=False, compare=False)

    def setPlan(self) -> None:
        """Mark the plan as planned, defaulting the date to today."""
        if self.date is None:
            self.date = dt.date.today()
        self.status = PLAN_PLANNED

    @staticmethod
    def _same_slot(a: Task, b: Task) -> bool:
        """True if `a` and `b` are the same care task: same pet, type, and start time."""
        return a.petId == b.petId and a.type == b.type and a.startMinutes() == b.startMinutes()

    def checkForTimeAvailability(
        self,
        durationHour: int,
        durationMinutes: int,
        earliestHour: int = 0,
        earliestMinutes: int = 0,
    ) -> tuple[int, int] | None:
        """Find the earliest free gap of the given duration at or after the earliest time.

        Walks the plan's tasks in start order, moving a cursor past each one. The first
        gap that is at least `duration` long, from the cursor to the next task's start,
        is the answer. Returns (hour, minutes) for the gap's start, or None if no gap
        fits before midnight.
        """
        duration = _duration_minutes(durationHour, durationMinutes)
        _check_hour_minutes(earliestHour, earliestMinutes, "earliest")
        cursor = earliestHour * 60 + earliestMinutes
        # arrayOfTasks is kept sorted by start time, so one pass finds the first gap.
        for task in self.arrayOfTasks:
            start, end = task.timeWindow()
            if start - cursor >= duration:
                break
            cursor = max(cursor, end)
        if cursor + duration > MINUTES_PER_DAY:
            return None
        return divmod(cursor, 60)

    def sort_by_time(self) -> None:
        """Sort arrayOfTasks in place by start hour, then start minutes.

        Uses the stored hour and minute fields directly as the sort key. Tasks
        without a start time sort as None and will fail the comparison, so the
        plan only holds timed tasks (addTasks enforces this).
        """
        self.arrayOfTasks[:] = sorted(
            self.arrayOfTasks, key=lambda t: (t.timeStartHour, t.timeStartMinutes)
        )

    def filter_tasks(
        self,
        status: str | None = None,
        pet_name: str | None = None,
        pets: Iterable[Pet] = (),
    ) -> list[Task]:
        """Return plan tasks matching `status` and/or the pet named `pet_name`.

        Pass None to skip a filter. Pet names match without regard to case, and `pets`
        supplies the petId -> name lookup. Results keep the plan's time order.
        """
        if status is not None and status not in (STATUS_PENDING, STATUS_INCOMPLETE, STATUS_COMPLETE):
            raise ValueError(f"status must be one of pending, incomplete, complete; got {status!r}")
        pet_ids = None
        if pet_name is not None:
            target = pet_name.strip().lower()
            pet_ids = {p.petId for p in pets if p.petName and p.petName.strip().lower() == target}
        return [
            task
            for task in self.arrayOfTasks
            if (status is None or task.status == status)
            and (pet_ids is None or task.petId in pet_ids)
        ]

    def _rebuild(self) -> None:
        """Rebuild arrayOfTasks greedily: highest priority first, keeping each task that fits.

        Ties go to the shorter task, then the earlier one. The result is always sorted by start.
        """
        def rank(task: Task) -> tuple[int, int, int]:
            """Sort key for the greedy pass: higher priority first, then shorter, then earlier."""
            start, end = task.timeWindow()
            return (-(task.priority or 0), end - start, start)

        selected: list[Task] = []
        for task in sorted(self._pool.values(), key=rank):
            if not any(_overlaps(task.timeWindow(), kept.timeWindow()) for kept in selected):
                selected.append(task)
        self.arrayOfTasks[:] = selected
        self.sort_by_time()

    def addTasks(self, task: Task) -> list[Task]:
        """Offer `task` to the plan and return the tasks it displaced.

        The task goes into the pool, then the whole plan is rebuilt by _rebuild().
        If the task survives the rebuild, the tasks that dropped out are returned as
        displaced. If it does not survive, it is removed from the pool, the plan is
        rebuilt again to its previous state, and ValueError is raised.

        Raises TypeError if `task` is not a Task. Raises ValueError if the task has
        no full time window, duplicates a task already offered (same pet, type, and
        start), or loses to higher-priority tasks it overlaps.
        """
        if not isinstance(task, Task):
            raise TypeError("task must be a Task")
        if self._pool.get(task.taskId) is task:
            return []
        if task.timeWindow() is None:
            raise ValueError(f"task {task.taskId} needs a start time and a duration or end time")
        if any(self._same_slot(task, other) for other in self._pool.values()):
            raise ValueError(f"task {task.taskId} duplicates an existing task for this pet")

        before = list(self.arrayOfTasks)
        self._pool[task.taskId] = task
        self._rebuild()
        kept = {id(t) for t in self.arrayOfTasks}
        if id(task) not in kept:
            # Rebuilding without the task restores the previous plan exactly.
            del self._pool[task.taskId]
            self._rebuild()
            raise ValueError(f"task {task.taskId} conflicts with higher-priority tasks in this plan")
        return [t for t in before if id(t) not in kept]

    def tryAddTask(self, task: Task) -> list[str]:
        """Offer `task` to the plan without raising on a conflict or duplicate.

        A wrapper around addTasks() that turns its ValueError into a message.
        Returns warning messages: empty if the task was added cleanly, one
        "Not scheduled:" message if it was rejected, and one "Bumped" message per
        task it displaced. A TypeError from a non-Task argument still propagates.
        """
        try:
            displaced = self.addTasks(task)
        except ValueError as err:
            return [f"Not scheduled: {err}"]
        return [
            f"Bumped by higher priority: {t.type} (task {t.taskId})" for t in displaced
        ]

    def removeTasks(self, taskId: int) -> None:
        """Remove the task with `taskId` from the plan, letting any bumped tasks return.

        Deletes the task from the pool and rebuilds the plan, so any task it had
        displaced is reconsidered and may return. Raises ValueError if the task is
        not in the pool.
        """
        if taskId not in self._pool:
            raise ValueError(f"task {taskId} is not in this plan")
        del self._pool[taskId]
        self._rebuild()

    def markPlanComplete(self) -> list[Task]:
        """Mark every task in the plan complete and the plan itself complete.

        Returns the next occurrences of any daily or weekly tasks. They are not added
        to this plan, because they belong to a later date's plan.
        """
        next_occurrences = []
        for task in self.arrayOfTasks:
            following = task.markTaskComplete()
            if following is not None:
                next_occurrences.append(following)
        self.status = PLAN_COMPLETE
        return next_occurrences

    def checkForCompletion(self) -> bool:
        """True if the plan has tasks and all of them are complete."""
        return bool(self.arrayOfTasks) and all(
            task.status == STATUS_COMPLETE for task in self.arrayOfTasks
        )

    def removePlan(self) -> None:
        """Clear the plan's tasks and mark it removed. The tasks themselves are kept."""
        self.arrayOfTasks.clear()
        self._pool.clear()
        self.status = PLAN_REMOVED
