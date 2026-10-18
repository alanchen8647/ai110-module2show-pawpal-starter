"""Terminal demo: build an owner, two pets, and a day's tasks, then print the schedule."""

import datetime as dt

from pawpal_system import PetOwner, Pet, Task, PlanSchedule


def make_pet(name, species, breed, age, gender, category):
    pet = Pet()
    pet.setName(name)
    pet.setSpecies(species)
    pet.setBreed(breed)
    pet.setAge(age)
    pet.setGender(gender)
    pet.setAnimalCategory(category)
    return pet


def make_task(pet, task_type, start, duration, priority, notes=None):
    task = Task()
    task.setType(task_type)
    task.setTimeStart(*start)
    task.setDuration(*duration)
    task.setPriority(priority)
    if notes:
        task.setOwnerPreferences(notes)
    pet.addTask(task)
    return task


def format_minutes(total):
    hour, minute = divmod(total, 60)
    return f"{hour:02d}:{minute:02d}"


def print_schedule(owner, plan):
    pets_by_id = {pet.petId: pet for pet in owner.pets}

    print(f"Today's Schedule ({plan.date}) for {owner.name}")
    print("-" * 60)
    for task in plan.arrayOfTasks:
        start, end = task.timeWindow()
        pet = pets_by_id[task.petId]
        print(f"{format_minutes(start)}-{format_minutes(end)}  {pet.petName:<8} {task.type:<10} priority {task.priority}")
        if task.ownerPreferences:
            print(f"                   note: {task.ownerPreferences}")
    print("-" * 60)


def main():
    owner = PetOwner()
    owner.setName("Alex")
    owner.setEmail("alex@example.com")
    owner.setPhone("555-0100")

    dog = make_pet("Rex", "Dog", "Beagle", 4, "male", "Mammal")
    cat = make_pet("Miso", "Cat", "Tabby", 2, "female", "Mammal")
    owner.addPet(dog)
    owner.addPet(cat)

    # Added out of time order on purpose: the plan keeps itself sorted on insert.
    plan = PlanSchedule()
    plan.setPlan()
    plan.addTasks(make_task(cat, "grooming", (18, 0), (0, 20), 2))
    walk = make_task(dog, "walk", (7, 30), (0, 30), 5, "Use the red leash")
    walk.setRecurrence("daily")
    walk.setDueDate(plan.date)
    plan.addTasks(walk)
    plan.addTasks(make_task(cat, "medication", (12, 0), (0, 5), 5, "Give with a treat"))
    plan.addTasks(make_task(dog, "feeding", (8, 0), (0, 15), 5, "Half cup of kibble"))

    # A conflicting task produces a warning instead of stopping the program.
    for warning in plan.tryAddTask(make_task(cat, "bath", (12, 2), (0, 10), 3)):
        print(f"Warning: {warning}")

    # Two tasks for different pets at the same time: equal priority, so the shorter one keeps the slot.
    print("Adding two tasks at 15:00:")
    for pet, ttype, duration in ((dog, "bath", (0, 30)), (cat, "play", (0, 20))):
        for warning in plan.tryAddTask(make_task(pet, ttype, (15, 0), duration, 4)):
            print(f"Warning: {warning}")

    # Mark the walk done so the status filter has something to separate.
    # The daily walk returns its next occurrence, which goes into tomorrow's plan.
    following = walk.markTaskComplete()
    tomorrow = PlanSchedule()
    tomorrow.date = plan.date + dt.timedelta(days=1)
    tomorrow.setPlan()
    tomorrow.addTasks(following)

    print("Schedule (sorted by time):")
    plan.sort_by_time()
    print_schedule(owner, plan)

    print("\nCompleted tasks:")
    for task in plan.filter_tasks(status="complete"):
        print(f"  {format_minutes(task.startMinutes())} {task.type} ({task.status})")

    print("\nPending tasks for Rex:")
    for task in plan.filter_tasks(status="pending", pet_name="Rex", pets=owner.pets):
        print(f"  {format_minutes(task.startMinutes())} {task.type}")

    print("\nTasks for Miso (any status):")
    for task in plan.filter_tasks(pet_name="miso", pets=owner.pets):
        print(f"  {format_minutes(task.startMinutes())} {task.type} ({task.status})")

    print(f"\nNext occurrence of the daily walk, due {following.dueDate}:")
    print(f"  {format_minutes(following.startMinutes())} {following.type} ({following.status}, {following.recurrence})")
    print(f"Tomorrow's plan ({tomorrow.date}) has {len(tomorrow.arrayOfTasks)} task(s).")


if __name__ == "__main__":
    main()
