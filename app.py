import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
**PawPal+** helps a pet owner plan care tasks for their pet(s) based on time, priority,
and preferences. Add pets, add tasks, and generate today's schedule.
"""
)

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner = st.session_state.owner
scheduler = Scheduler(owner=owner)

st.subheader("Owner & Pet")
owner.name = st.text_input("Owner name", value=owner.name)

col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if owner.get_pet(pet_name) is None:
        owner.add_pet(Pet(name=pet_name, species=species))
        st.success(f"Added {pet_name} the {species}.")
    else:
        st.warning(f"{pet_name} is already added.")

if not owner.pets:
    st.info("No pets yet. Add one above.")
else:
    st.write("Pets:", ", ".join(p.name for p in owner.pets))

st.divider()

st.subheader("Tasks")

if owner.pets:
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        target_pet = st.selectbox("Pet", [p.name for p in owner.pets])
    with col2:
        task_title = st.text_input("Task title", value="Morning walk")
    with col3:
        task_time = st.text_input("Time (HH:MM)", value="08:00")
    with col4:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col5:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

    if st.button("Add task"):
        pet = owner.get_pet(target_pet)
        pet.add_task(
            Task(
                title=task_title,
                time=task_time,
                duration_minutes=int(duration),
                priority=priority,
                frequency=frequency,
            )
        )
        st.success(f"Added '{task_title}' for {target_pet} at {task_time}.")
else:
    st.info("Add a pet before adding tasks.")

st.divider()

st.subheader("Today's Schedule")

if st.button("Generate schedule"):
    st.session_state.show_schedule = True

if st.session_state.get("show_schedule"):
    plan = scheduler.build_daily_plan()

    if not plan:
        st.info("No pending tasks for today.")
    else:
        rows = [
            {
                "Time": t.time,
                "Task": t.title,
                "Pet": t.pet_name,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority,
                "Frequency": t.frequency,
            }
            for t in plan
        ]
        st.table(rows)

        conflicts = scheduler.detect_conflicts(plan)
        for warning in conflicts:
            st.warning(f"⚠️ {warning}")

    st.markdown("### Mark a task complete")
    for task in plan:
        if st.button(f"Mark done: {task.time} {task.title} ({task.pet_name})", key=id(task)):
            scheduler.complete_task(task)
            st.rerun()
