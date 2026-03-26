import streamlit as st
from pawpal_system import Owner, Pet, CareTask, Scheduler, save_to_json, load_from_json

PRIORITY_BADGE = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}

TASK_EMOJI = {
    "walk":       "🦮",
    "feeding":    "🍽️",
    "feed":       "🍽️",
    "meds":       "💊",
    "medication": "💊",
    "grooming":   "✂️",
    "groom":      "✂️",
    "play":       "🎾",
    "litter":     "🧹",
    "enrichment": "🧩",
    "laser":      "🔦",
}

def task_emoji(title: str) -> str:
    lower = title.lower()
    for keyword, icon in TASK_EMOJI.items():
        if keyword in lower:
            return icon
    return "📋"

DATA_FILE = "data.json"

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("A daily pet care planner that schedules tasks based on priority and your available time.")

# --- Load persisted data once per session ---
if "loaded" not in st.session_state:
    try:
        _owner, _pet, _tasks = load_from_json(DATA_FILE)
        st.session_state.tasks        = [t.to_dict() for t in _tasks]
        st.session_state.saved_owner  = _owner.name
        st.session_state.saved_avail  = _owner.available_mins
        st.session_state.saved_pet    = _pet.name
        st.session_state.saved_species = _pet.species
        st.session_state.saved_age    = _pet.age
    except FileNotFoundError:
        st.session_state.tasks = []
        st.session_state.saved_owner  = "Jordan"
        st.session_state.saved_avail  = 60
        st.session_state.saved_pet    = "Mochi"
        st.session_state.saved_species = "dog"
        st.session_state.saved_age    = 3
    st.session_state.loaded = True


def _save(owner_name, available_mins, pet_name, species, age):
    """Persist current state to data.json."""
    save_to_json(
        Owner(name=owner_name, available_mins=int(available_mins)),
        Pet(name=pet_name, species=species, age=int(age)),
        [task_from_dict(t) for t in st.session_state.tasks],
        DATA_FILE,
    )


# --- Owner & Pet Info ---
st.subheader("Owner & Pet Info")
col1, col2 = st.columns(2)
with col1:
    owner_name    = st.text_input("Owner name", value=st.session_state.saved_owner)
    available_mins = st.number_input("Time available today (minutes)", min_value=1, max_value=480,
                                     value=st.session_state.saved_avail)
with col2:
    pet_name = st.text_input("Pet name", value=st.session_state.saved_pet)
    species  = st.selectbox("Species", ["dog", "cat", "other"],
                            index=["dog", "cat", "other"].index(st.session_state.saved_species))
    age      = st.number_input("Pet age (years)", min_value=0, max_value=30,
                               value=st.session_state.saved_age)

st.divider()

# --- Task Management ---
st.subheader("Add a Task")


def task_from_dict(t: dict) -> CareTask:
    """Construct a CareTask from a session-state dict, tolerating missing or extra keys."""
    return CareTask(
        title=t["title"],
        duration_mins=t["duration_mins"],
        priority=t["priority"],
        preferred_time=t.get("preferred_time"),
        start_time=t.get("start_time"),
        completed=t.get("completed", False),
        frequency=t.get("frequency"),
        pet_name=t.get("pet_name"),
    )

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
        _save(owner_name, available_mins, pet_name, species, age)
        st.success(f"Added: {task_title.strip()} (saved)")

st.divider()

# --- Task List ---
st.subheader("Current Tasks")

if st.session_state.tasks:
    # Build scheduler just for display methods
    _owner = Owner(name=owner_name, available_mins=int(available_mins))
    _pet   = Pet(name=pet_name, species=species, age=int(age))
    _sched = Scheduler(owner=_owner, pet=_pet)
    for t in st.session_state.tasks:
        _sched.add_task(task_from_dict(t))

    # Conflict warnings shown immediately
    conflicts = _sched.detect_conflicts()
    for warning in conflicts:
        st.warning(warning)

    # Toggle sort mode
    sort_mode = st.radio(
        "View order",
        ["Priority then time", "By start time", "By insertion order"],
        horizontal=True,
    )
    if sort_mode == "Priority then time":
        display_tasks = _sched.sort_by_priority_then_time()
    elif sort_mode == "By start time":
        display_tasks = _sched.sort_by_time()
    else:
        display_tasks = _sched.tasks

    table_data = [
        {
            "Priority": PRIORITY_BADGE.get(t.priority, t.priority),
            "Title": f"{task_emoji(t.title)}  {t.title}",
            "Duration (min)": t.duration_mins,
            "Start time": t.start_time or "—",
            "Preferred": t.preferred_time or "any",
            "Repeats": t.frequency or "—",
        }
        for t in display_tasks
    ]
    st.dataframe(table_data, hide_index=True, use_container_width=True)

    if st.button("Clear all tasks"):
        st.session_state.tasks = []
        _save(owner_name, available_mins, pet_name, species, age)
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
            scheduler.add_task(task_from_dict(t))

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

        # Scheduled tasks table — priority then time order
        if plan.scheduled:
            st.subheader("Scheduled Tasks")
            scheduled_set = set(id(t) for t in plan.scheduled)
            st.dataframe([
                {
                    "Priority": PRIORITY_BADGE.get(t.priority, t.priority),
                    "Task": f"{task_emoji(t.title)}  {t.title}",
                    "Duration (min)": t.duration_mins,
                    "Start time": t.start_time or "—",
                    "Repeats": t.frequency or "—",
                }
                for t in scheduler.sort_by_priority_then_time()
                if id(t) in scheduled_set
            ], hide_index=True, use_container_width=True)

        # Skipped tasks
        if plan.skipped:
            st.subheader("Skipped Tasks")
            st.caption("These tasks did not fit within your available time.")
            for task in plan.skipped:
                badge = PRIORITY_BADGE.get(task.priority, task.priority)
                st.error(f"{badge}  {task.title} — {task.duration_mins} min", icon="🚫")

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
