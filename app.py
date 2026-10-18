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

# The owner and the day's plan live in session_state so they survive reruns.
if "owner" not in st.session_state:
    st.session_state.owner = PetOwner()
    st.session_state.plan = PlanSchedule()
    st.session_state.plan.setPlan()
owner = st.session_state.owner
plan = st.session_state.plan

st.subheader("Owner and Pets")
owner_name = st.text_input("Owner name", value="Jordan")
if owner_name.strip() and owner.name != owner_name.strip():
    owner.setName(owner_name)

pet_col1, pet_col2 = st.columns(2)
with pet_col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with pet_col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    try:
        pet = Pet()
        pet.setName(pet_name)
        pet.setSpecies(species)
        owner.addPet(pet)
    except ValueError as err:
        st.error(str(err))

if owner.pets:
    st.write("Pets: " + ", ".join(f"{p.petName} ({p.petSpecies})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Schedule a Task")
if not owner.pets:
    st.info("Add a pet before scheduling a task.")
else:
    task_pet = st.selectbox("For pet", owner.pets, format_func=lambda p: p.petName)

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
            displaced = plan.addTasks(task)
            task_pet.addTask(task)
        except ValueError as err:
            st.error(str(err))
        else:
            st.success(f"Added {task.type} for {task_pet.petName}.")
            if displaced:
                names = {p.petId: p.petName for p in owner.pets}
                st.warning(
                    "Bumped by higher priority: "
                    + ", ".join(f"{t.type} for {names[t.petId]}" for t in displaced)
                )

st.divider()

st.subheader("Today's Schedule")
if plan.arrayOfTasks:
    pets_by_id = {p.petId: p for p in owner.pets}
    rows = []
    for task in plan.arrayOfTasks:
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
    st.table(rows)
    st.caption(f"{len(rows)} task(s) planned for {plan.date}.")
else:
    st.info("No tasks scheduled yet. Add one above.")
