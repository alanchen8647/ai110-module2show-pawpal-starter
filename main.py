"""Terminal demo: build an owner, two pets, and a day's tasks, then print the schedule."""

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
    for task in sorted(plan.arrayOfTasks, key=lambda t: t.startMinutes()):
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

    tasks = [
        make_task(dog, "walk", (7, 30), (0, 30), 5, "Use the red leash"),
        make_task(dog, "feeding", (8, 0), (0, 15), 5, "Half cup of kibble"),
        make_task(cat, "medication", (12, 0), (0, 5), 5, "Give with a treat"),
        make_task(cat, "grooming", (18, 0), (0, 20), 2),
    ]

    plan = PlanSchedule()
    plan.setPlan()
    for task in tasks:
        plan.addTasks(task)

    print_schedule(owner, plan)


if __name__ == "__main__":
    main()
