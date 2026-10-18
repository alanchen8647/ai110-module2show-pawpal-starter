"""PawPal+ domain model skeleton.

Classes mirror diagrams/uml.mmd. Attributes are dataclass fields; methods are
stubs that raise NotImplementedError until the logic is implemented.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field


@dataclass
class PetOwner:
    """A pet owner (client) who owns pets and tasks."""

    clientId: int | None = None
    name: str | None = None
    email: str | None = None
    phone: str | None = None

    def addClient(self, client: PetOwner) -> None:
        raise NotImplementedError

    def setName(self, name: str) -> None:
        raise NotImplementedError

    def setEmail(self, email: str) -> None:
        raise NotImplementedError

    def setPhone(self, phone: str) -> None:
        raise NotImplementedError

    def removeClient(self, clientId: int) -> None:
        raise NotImplementedError


@dataclass
class Pet:
    """A pet belonging to a PetOwner."""

    petId: int | None = None
    petName: str | None = None
    petSpecies: str | None = None
    breed: str | None = None
    age: int | None = None
    ownerId: int | None = None
    gender: str | None = None
    animalCategory: str | None = None

    def createPet(self) -> Pet:
        raise NotImplementedError

    def setName(self, name: str) -> None:
        raise NotImplementedError

    def setSpecies(self, species: str) -> None:
        raise NotImplementedError

    def setBreed(self, breed: str) -> None:
        raise NotImplementedError

    def setAge(self, age: int) -> None:
        raise NotImplementedError

    def setOwnerId(self, ownerId: int) -> None:
        raise NotImplementedError

    def setGender(self, gender: str) -> None:
        raise NotImplementedError

    def setAnimalCategory(self, category: str) -> None:
        raise NotImplementedError


@dataclass
class Task:
    """A single care task (walk, feeding, meds, grooming, ...) for a pet."""

    taskId: int | None = None
    petId: int | None = None
    ownerId: int | None = None
    status: str | None = None
    type: str | None = None
    time: dt.datetime | None = None
    timeStart: dt.time | None = None
    timeEnd: dt.time | None = None
    priority: int | None = None
    ownerPreferences: str | None = None

    def createTasks(self) -> Task:
        raise NotImplementedError

    def setPet(self, petId: int) -> None:
        raise NotImplementedError

    def setOwner(self, ownerId: int) -> None:
        raise NotImplementedError

    def markComplete(self) -> None:
        raise NotImplementedError

    def markIncomplete(self) -> None:
        raise NotImplementedError

    def markPending(self) -> None:
        raise NotImplementedError

    def setType(self, type: str) -> None:
        raise NotImplementedError

    def setTime(self, time: dt.datetime) -> None:
        raise NotImplementedError

    def setPriority(self, priority: int) -> None:
        raise NotImplementedError

    def setOwnerPreferences(self, preferences: str) -> None:
        raise NotImplementedError


@dataclass
class PlanSchedule:
    """A daily plan: an ordered selection of tasks for one date."""

    planId: int | None = None
    date: dt.date | None = None
    arrayOfTasks: list[Task] = field(default_factory=list)
    status: str | None = None

    def setPlan(self) -> None:
        raise NotImplementedError

    def checkForTimeAvailability(self, start: dt.time, end: dt.time) -> bool:
        raise NotImplementedError

    def addTasks(self, task: Task) -> None:
        raise NotImplementedError

    def removeTasks(self, taskId: int) -> None:
        raise NotImplementedError

    def markComplete(self) -> None:
        raise NotImplementedError

    def checkForCompletion(self) -> bool:
        raise NotImplementedError

    def removePlan(self) -> None:
        raise NotImplementedError
