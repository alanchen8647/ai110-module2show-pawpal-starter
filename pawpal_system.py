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
from dataclasses import dataclass, field

MINUTES_PER_DAY = 24 * 60
MIN_PRIORITY = 1
MAX_PRIORITY = 5

STATUS_PENDING = "pending"
STATUS_INCOMPLETE = "incomplete"
STATUS_COMPLETE = "complete"

PLAN_PLANNED = "planned"
PLAN_COMPLETE = "complete"
PLAN_REMOVED = "removed"

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

    def createTasks(self) -> Task:
        """Return a new, unscheduled task with an auto-generated ID."""
        return Task()

    def setPet(self, petId: int) -> None:
        """Set the ID of the pet this task belongs to."""
        self.petId = _check_int(petId, "petId", 1, 10**9)

    def markTaskComplete(self) -> None:
        """Set the task's status to complete."""
        self.status = STATUS_COMPLETE

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
        _check_hour_minutes(hour, minutes, "duration")
        if hour * 60 + minutes == 0:
            raise ValueError("duration must be greater than 0")
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

    def setPlan(self) -> None:
        """Mark the plan as planned, defaulting the date to today."""
        if self.date is None:
            self.date = dt.date.today()
        self.status = PLAN_PLANNED

    def _overlapping(self, start: int, end: int, ignore: Task | None = None) -> bool:
        """True if [start, end) overlaps any timed task in the plan (except `ignore`)."""
        for task in self.arrayOfTasks:
            if task is ignore:
                continue
            window = task.timeWindow()
            if window is None:
                continue
            if start < window[1] and window[0] < end:
                return True
        return False

    def checkForTimeAvailability(
        self, startHour: int, startMinutes: int, durationHour: int, durationMinutes: int
    ) -> bool:
        """True if a slot starting at the given time with the given duration fits the day."""
        _check_hour_minutes(startHour, startMinutes, "start")
        _check_hour_minutes(durationHour, durationMinutes, "duration")
        duration = durationHour * 60 + durationMinutes
        if duration == 0:
            raise ValueError("duration must be greater than 0")
        start = startHour * 60 + startMinutes
        end = start + duration
        if end > MINUTES_PER_DAY:
            return False
        return not self._overlapping(start, end)

    def addTasks(self, task: Task) -> None:
        """Add `task` to the plan. Raises if its time overlaps another task in the plan."""
        if not isinstance(task, Task):
            raise TypeError("task must be a Task")
        if any(t is task for t in self.arrayOfTasks):
            return
        window = task.timeWindow()
        if window is not None and self._overlapping(window[0], window[1], ignore=task):
            raise ValueError(f"task {task.taskId} overlaps another task in this plan")
        self.arrayOfTasks.append(task)

    def removeTasks(self, taskId: int) -> None:
        """Remove the task with `taskId` from the plan."""
        for index, task in enumerate(self.arrayOfTasks):
            if task.taskId == taskId:
                del self.arrayOfTasks[index]
                return
        raise ValueError(f"task {taskId} is not in this plan")

    def markPlanComplete(self) -> None:
        """Mark every task in the plan complete and the plan itself complete."""
        for task in self.arrayOfTasks:
            task.markTaskComplete()
        self.status = PLAN_COMPLETE

    def checkForCompletion(self) -> bool:
        """True if the plan has tasks and all of them are complete."""
        return bool(self.arrayOfTasks) and all(
            task.status == STATUS_COMPLETE for task in self.arrayOfTasks
        )

    def removePlan(self) -> None:
        """Clear the plan's tasks and mark it removed. The tasks themselves are kept."""
        self.arrayOfTasks.clear()
        self.status = PLAN_REMOVED
