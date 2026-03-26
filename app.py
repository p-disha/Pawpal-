import streamlit as st
from pawpal_system import Owner, Pet, CareTask, Scheduler

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
st.subheader("Add a Task")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
    preferred_time = st.selectbox("Preferred time", ["any", "morning", "afternoon", "evening"])
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    start_time = st.text_input("Start time (HH:MM, optional)", value="", placeholder="e.g. 08:00")
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    frequency = st.selectbox("Repeats", ["none", "daily", "weekly"])

if st.button("Add task", type="primary"):
    if not task_title.strip():
        st.warning("Task title cannot be empty.")
    else:
        st.session_state.tasks.append({
            "title": task_title.strip(),
            "duration_mins": int(duration),
            "priority": priority,
            "preferred_time": None if preferred_time == "any" else preferred_time,
            "start_time": start_time.strip() if start_time.strip() else None,
            "frequency": None if frequency == "none" else frequency,
            "pet_name": pet_name.strip(),
        })
        st.success(f"Added: {task_title.strip()}")

st.divider()

# --- Task List ---
st.subheader("Current Tasks")

if st.session_state.tasks:
    # Build scheduler just for display methods
    _owner = Owner(name=owner_name, available_mins=int(available_mins))
    _pet   = Pet(name=pet_name, species=species, age=int(age))
    _sched = Scheduler(owner=_owner, pet=_pet)
    for t in st.session_state.tasks:
        _sched.add_task(CareTask(**t))

    # Conflict warnings shown immediately
    conflicts = _sched.detect_conflicts()
    for warning in conflicts:
        st.warning(warning)

    # Toggle: sort by time vs insertion order
    sort_mode = st.radio("View order", ["By start time", "By insertion order"], horizontal=True)
    display_tasks = _sched.sort_by_time() if sort_mode == "By start time" else _sched.tasks

    table_data = [
        {
            "Title": t.title,
            "Duration (min)": t.duration_mins,
            "Priority": t.priority,
            "Start time": t.start_time or "—",
            "Preferred": t.preferred_time or "any",
            "Repeats": t.frequency or "—",
        }
        for t in display_tasks
    ]
    st.table(table_data)

    if st.button("Clear all tasks"):
        st.session_state.tasks = []
        st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Schedule Generation ---
st.subheader("Generate Schedule")

if st.button("Generate schedule", type="primary"):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        owner = Owner(name=owner_name, available_mins=int(available_mins))
        pet   = Pet(name=pet_name, species=species, age=int(age))
        scheduler = Scheduler(owner=owner, pet=pet)

        for t in st.session_state.tasks:
            scheduler.add_task(CareTask(**t))

        # Conflict detection
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.subheader("Scheduling Conflicts")
            for warning in conflicts:
                st.warning(warning)

        # Build priority-based plan
        plan = scheduler.build_plan()
        total_scheduled = sum(t.duration_mins for t in plan.scheduled)

        st.success(
            f"Plan ready for {pet_name}  |  "
            f"{len(plan.scheduled)} tasks scheduled  |  "
            f"{total_scheduled} / {available_mins} min used"
        )

        # Scheduled tasks table
        if plan.scheduled:
            st.subheader("Scheduled Tasks")
            st.table([
                {
                    "Task": t.title,
                    "Duration (min)": t.duration_mins,
                    "Priority": t.priority,
                    "Start time": t.start_time or "—",
                    "Repeats": t.frequency or "—",
                }
                for t in scheduler.sort_by_time()
                if t in plan.scheduled
            ])

        # Skipped tasks
        if plan.skipped:
            st.subheader("Skipped Tasks")
            st.caption("These tasks did not fit within your available time.")
            for task in plan.skipped:
                st.error(
                    f"{task.title} — {task.duration_mins} min | priority: {task.priority}",
                    icon="🚫",
                )

        # Explanation
        with st.expander("View explanation", expanded=False):
            st.markdown(plan.explain())

        # Filter view
        st.subheader("Filter Tasks")
        col_a, col_b = st.columns(2)
        with col_a:
            show_pending = scheduler.filter_tasks(completed=False)
            st.metric("Pending tasks", len(show_pending))
        with col_b:
            st.metric("Total tasks", len(scheduler.tasks))
