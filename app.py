import streamlit as st
from pawpal import Owner, Pet, CareTask, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("A daily pet care planner that schedules tasks based on priority and your available time.")

# --- Owner & Pet Info ---
st.subheader("Owner & Pet Info")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_mins = st.number_input("Time available today (minutes)", min_value=1, max_value=480, value=60)
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Pet age (years)", min_value=0, max_value=30, value=3)

st.divider()

# --- Task Management ---
st.subheader("Tasks")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    preferred_time = st.selectbox("Preferred time", ["any", "morning", "afternoon", "evening"])

if st.button("Add task"):
    if task_title.strip():
        st.session_state.tasks.append({
            "title": task_title.strip(),
            "duration_mins": int(duration),
            "priority": priority,
            "preferred_time": None if preferred_time == "any" else preferred_time,
        })
    else:
        st.warning("Task title cannot be empty.")

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
    if st.button("Clear all tasks"):
        st.session_state.tasks = []
        st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Schedule Generation ---
st.subheader("Generate Schedule")

if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        owner = Owner(name=owner_name, available_mins=int(available_mins))
        pet = Pet(name=pet_name, species=species, age=int(age))
        scheduler = Scheduler(owner=owner, pet=pet)

        for t in st.session_state.tasks:
            scheduler.add_task(CareTask(
                title=t["title"],
                duration_mins=t["duration_mins"],
                priority=t["priority"],
                preferred_time=t["preferred_time"],
            ))

        plan = scheduler.build_plan()

        st.success(f"Plan generated for {pet_name} ({owner_name} has {available_mins} min today)")

        if plan.scheduled:
            st.markdown("### Scheduled Tasks")
            for task in plan.scheduled:
                st.markdown(f"- **{task.title}** — {task.duration_mins} min | priority: `{task.priority}`")

        if plan.skipped:
            st.markdown("### Skipped Tasks _(not enough time)_")
            for task in plan.skipped:
                st.markdown(f"- {task.title} — {task.duration_mins} min | priority: `{task.priority}`")

        st.markdown("### Explanation")
        st.markdown(plan.explain())
