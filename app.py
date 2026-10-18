import datetime as dt

import streamlit as st

from pawpal_system import Pet, PetOwner, PlanSchedule, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Owners and the day's plan live in session_state so they survive reruns.
if "owners" not in st.session_state:
    st.session_state.owners = []
    st.session_state.plan = PlanSchedule()
    st.session_state.plan.setPlan()
owners = st.session_state.owners
plan = st.session_state.plan
# Tasks that did not fit in the plan, with the reason. Kept so they are not lost.
if "unscheduled" not in st.session_state:
    st.session_state.unscheduled = []
unscheduled = st.session_state.unscheduled


def forget_tasks(pets):
    """Remove the tasks of `pets` from the plan and from the unscheduled list."""
    pet_ids = {p.petId for p in pets}
    for pet in pets:
        for task in pet.tasks:
            try:
                plan.removeTasks(task.taskId)
            except ValueError:
                pass  # this task is not in the plan
    unscheduled[:] = [(t, reason) for t, reason in unscheduled if t.petId not in pet_ids]


st.subheader("Create Owner")
owner_col1, owner_col2, owner_col3 = st.columns(3)
with owner_col1:
    owner_name = st.text_input("Owner name", placeholder="e.g. Jordan")
with owner_col2:
    owner_email = st.text_input("Owner email (optional)", placeholder="name@example.com")
with owner_col3:
    owner_phone = st.text_input("Owner phone (optional)", placeholder="555-0100")

if st.button("Add owner"):
    try:
        new_owner = PetOwner()
        new_owner.setName(owner_name)
        if owner_email.strip():
            new_owner.setEmail(owner_email)
        if owner_phone.strip():
            new_owner.setPhone(owner_phone)
        owners.append(new_owner)
    except ValueError as err:
        st.error(str(err))
    else:
        st.success(f"Added owner {new_owner.name}.")

st.subheader("Owners")
# The table is filled at the end of the pet section, so it shows pets added in this run.
owner_slot = st.container()
if owners:
    owner_pick = st.selectbox(
        "Owner to remove", range(len(owners)), format_func=lambda i: owners[i].name
    )
    if st.button("Remove owner"):
        removed_owner = owners[owner_pick]
        # Removing an owner also removes its pets, so their tasks leave the plan too.
        forget_tasks(removed_owner.pets)
        removed_owner.removeClient(removed_owner.clientId)
        owners[:] = [o for o in owners if o is not removed_owner]
        st.rerun()

st.divider()

st.subheader("Create Pet")
if not owners:
    st.info("Add an owner before adding a pet.")
else:
    # Streamlit returns a copy of a selected object, so pick an index and look up the real owner.
    owner_index = st.selectbox(
        "Owner", range(len(owners)), format_func=lambda i: owners[i].name
    )
    pet_owner = owners[owner_index]

    pet_col1, pet_col2, pet_col3 = st.columns(3)
    with pet_col1:
        pet_name = st.text_input("Pet name", placeholder="e.g. Mochi")
    with pet_col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with pet_col3:
        breed = st.text_input("Breed (optional)")

    pet_col4, pet_col5, pet_col6 = st.columns(3)
    with pet_col4:
        age = st.number_input("Age (years)", min_value=0, max_value=100, value=0)
    with pet_col5:
        gender = st.selectbox("Gender", ["unknown", "female", "male"])
    with pet_col6:
        category = st.text_input("Animal category (optional)", placeholder="e.g. mammal")

    if st.button("Add pet"):
        try:
            pet = Pet()
            pet.setName(pet_name)
            pet.setSpecies(species)
            if breed.strip():
                pet.setBreed(breed)
            pet.setAge(int(age))
            pet.setGender(gender)
            if category.strip():
                pet.setAnimalCategory(category)
            pet_owner.addPet(pet)
        except ValueError as err:
            st.error(str(err))
        else:
            st.success(f"Added {pet.petName} for {pet_owner.name}.")

# Built after the forms so pets added in this run are included.
all_pets = [pet for o in owners for pet in o.pets]
pets_by_id = {p.petId: p for p in all_pets}
owner_of = {p.petId: o for o in owners for p in o.pets}

st.subheader("Owners and Pets")
if all_pets:
    # One row per pet, with the owner's details at the end of each row.
    pet_rows = [
        {
            "Pet ID": str(p.petId),
            "Pet": p.petName,
            "Species": p.petSpecies,
            "Breed": p.breed or "",
            "Age": str(p.age),
            "Gender": p.gender or "",
            "Category": p.animalCategory or "",
            "Owner": owner_of[p.petId].name,
            "Email": owner_of[p.petId].email or "",
            "Phone": owner_of[p.petId].phone or "",
        }
        for p in all_pets
    ]
    st.dataframe(pet_rows, hide_index=True)
    pet_pick = st.selectbox(
        "Pet to remove",
        range(len(all_pets)),
        format_func=lambda i: f"{all_pets[i].petName} ({owner_of[all_pets[i].petId].name})",
    )
    if st.button("Remove pet"):
        removed_pet = all_pets[pet_pick]
        forget_tasks([removed_pet])
        removed_pet.removePet()
        st.rerun()
else:
    st.info("No pets yet. Add one above.")

with owner_slot:
    owner_rows = [
        {
            "Owner": o.name,
            "Email": o.email or "",
            "Phone": o.phone or "",
            "Pets": ", ".join(p.petName for p in o.pets) or "No pets",
        }
        for o in owners
    ]
    if owner_rows:
        st.dataframe(owner_rows, hide_index=True)
    else:
        st.info("No owners yet. Add one above.")

st.divider()

st.subheader("Schedule a Task")
if not all_pets:
    st.info("Add a pet before scheduling a task.")
else:
    # Pick an index so the task is attached to the real pet, not a copy.
    pet_index = st.selectbox(
        "For pet",
        range(len(all_pets)),
        format_func=lambda i: f"{all_pets[i].petName} ({owner_of[all_pets[i].petId].name})",
    )
    task_pet = all_pets[pet_index]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_type = st.text_input("Task type", value="walk")
    with col2:
        start = st.time_input("Start time", value=dt.time(9, 0))
    with col3:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col4:
        priority = st.number_input("Priority (1-5)", min_value=1, max_value=5, value=5)
    notes = st.text_input("Owner note (optional)")

    if st.button("Add task"):
        try:
            task = Task()
            task.setType(task_type)
            task.setTimeStart(start.hour, start.minute)
            task.setDuration(*divmod(int(duration), 60))
            task.setPriority(int(priority))
            if notes.strip():
                task.setOwnerPreferences(notes)
            # The plan checks for duplicates by pet, so the task needs its petId before it is offered.
            task.setPet(task_pet.petId)
        except ValueError as err:
            st.error(str(err))
        else:
            # Attach the task to its pet whether or not it fits, so it is always stored.
            task_pet.addTask(task)
            try:
                displaced = plan.addTasks(task)
            except ValueError as err:
                unscheduled.append((task, str(err)))
                st.warning(f"Saved {task.type} for {task_pet.petName} as unscheduled: {err}")
            else:
                st.success(f"Added {task.type} for {task_pet.petName}.")
                if displaced:
                    st.warning(
                        "Bumped by higher priority: "
                        + ", ".join(f"{t.type} for {pets_by_id[t.petId].petName}" for t in displaced)
                    )

st.divider()

st.subheader("Today's Schedule")
if plan.arrayOfTasks:
    if st.button("Mark plan complete"):
        # Runs before the table so this run shows the updated statuses.
        following = plan.markPlanComplete()
        st.success("Plan marked complete.")
        if following:
            st.info(
                "Next occurrences: "
                + ", ".join(
                    f"{t.type} for {pets_by_id[t.petId].petName} on {t.dueDate}" for t in following
                )
            )

    met1, met2, met3, met4 = st.columns(4)
    met1.metric("Total", len(plan.arrayOfTasks))
    met2.metric("Pending", len(plan.filter_tasks(status="pending")))
    met3.metric("Incomplete", len(plan.filter_tasks(status="incomplete")))
    met4.metric("Complete", len(plan.filter_tasks(status="complete")))

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        status_choice = st.selectbox("Show status", ["all", "pending", "incomplete", "complete"])
    with filter_col2:
        pet_choice = st.selectbox("Show pet", ["all"] + [p.petName for p in all_pets])

    visible = plan.filter_tasks(
        status=None if status_choice == "all" else status_choice,
        pet_name=None if pet_choice == "all" else pet_choice,
        pets=all_pets,
    )
    if visible:
        rows = []
        for task in visible:
            start_m, end_m = task.timeWindow()
            rows.append(
                {
                    "Time": f"{start_m // 60:02d}:{start_m % 60:02d}-{end_m // 60:02d}:{end_m % 60:02d}",
                    "Pet": pets_by_id[task.petId].petName,
                    "Task": task.type,
                    "Priority": task.priority,
                    "Status": task.status,
                    "Owner note": task.ownerPreferences or "",
                }
            )
        st.dataframe(
            rows,
            hide_index=True,
            column_config={
                "Time": st.column_config.TextColumn("Time", width="small"),
                "Priority": st.column_config.ProgressColumn(
                    "Priority", min_value=1, max_value=5, format="%d"
                ),
                "Status": st.column_config.TextColumn("Status", width="small"),
                "Owner note": st.column_config.TextColumn("Owner note", width="large"),
            },
        )
    else:
        st.info("No tasks match these filters.")
    st.caption(f"Showing {len(visible)} of {len(plan.arrayOfTasks)} task(s) for {plan.date}.")
    if plan.checkForCompletion():
        st.success("Every task in today's plan is complete.")
    elif plan.filter_tasks(status="incomplete"):
        st.warning(
            f"{len(plan.filter_tasks(status='incomplete'))} task(s) were marked incomplete and still need attention."
        )
else:
    st.info("No tasks scheduled yet. Add one above.")

st.divider()

st.subheader("Unscheduled Tasks")
if unscheduled:
    unscheduled_rows = []
    for task, reason in unscheduled:
        start_m, end_m = task.timeWindow()
        unscheduled_rows.append(
            {
                "Time": f"{start_m // 60:02d}:{start_m % 60:02d}-{end_m // 60:02d}:{end_m % 60:02d}",
                "Pet": pets_by_id[task.petId].petName,
                "Task": task.type,
                "Priority": task.priority,
                "Reason": reason,
            }
        )
    st.dataframe(unscheduled_rows, hide_index=True)
else:
    st.caption("Tasks that do not fit the plan will be listed here.")
