import sys
sys.stdout.reconfigure(encoding="utf-8")

from tabulate import tabulate
from pawpal_system import Owner, Pet, CareTask, Scheduler

# ── Emoji helpers ─────────────────────────────────────────────────────────────

PRIORITY_ICON = {"high": "🔴", "medium": "🟡", "low": "🟢"}
SPECIES_ICON  = {"dog": "🐶", "cat": "🐱", "other": "🐾"}
FREQ_ICON     = {"daily": "🔁", "weekly": "📅", None: ""}
STATUS_ICON   = {True: "✅", False: "⬜"}

TASK_EMOJI = {
    "walk":        "🦮",
    "feeding":     "🍽️",
    "feed":        "🍽️",
    "meds":        "💊",
    "medication":  "💊",
    "grooming":    "✂️",
    "groom":       "✂️",
    "play":        "🎾",
    "litter":      "🧹",
    "enrichment":  "🧩",
    "laser":       "🔦",
}

def task_emoji(title: str) -> str:
    lower = title.lower()
    for keyword, icon in TASK_EMOJI.items():
        if keyword in lower:
            return icon
    return "📋"


def priority_badge(priority: str) -> str:
    return f"{PRIORITY_ICON.get(priority, '⚪')} {priority.capitalize()}"


def section(title: str, width: int = 62) -> None:
    print()
    print("━" * width)
    print(f"  {title}")
    print("━" * width)


# ── Setup ─────────────────────────────────────────────────────────────────────

owner = Owner(name="Jordan", available_mins=90)
pet1  = Pet(name="Mochi", species="dog", age=3)
pet2  = Pet(name="Luna",  species="cat", age=5)

scheduler = Scheduler(owner=owner, pet=pet1)

scheduler.add_task(CareTask("Evening walk",    duration_mins=30, priority="medium", start_time="18:00", pet_name="Mochi"))
scheduler.add_task(CareTask("Feeding",         duration_mins=10, priority="high",   start_time="07:30", pet_name="Mochi", frequency="daily"))
scheduler.add_task(CareTask("Grooming",        duration_mins=20, priority="medium", start_time="14:00", pet_name="Mochi", frequency="weekly"))
scheduler.add_task(CareTask("Morning walk",    duration_mins=30, priority="high",   start_time="08:00", pet_name="Mochi"))
scheduler.add_task(CareTask("Litter box",      duration_mins=10, priority="medium", start_time="08:00", pet_name="Luna"))
scheduler.add_task(CareTask("Laser play",      duration_mins=15, priority="low",    start_time="19:00", pet_name="Luna"))
scheduler.add_task(CareTask("Enrichment play", duration_mins=40, priority="low",    pet_name="Mochi"))

# ── Header ────────────────────────────────────────────────────────────────────

print()
print("=" * 62)
print(f"   🐾  PawPal+  —  Daily Pet Care Planner")
print(f"   👤  Owner : {owner.name}  |  ⏱  Available : {owner.available_mins} min")
print(f"   {SPECIES_ICON.get(pet1.species, '🐾')}  Pet   : {pet1.name} ({pet1.species}, age {pet1.age})")
print("=" * 62)

# ── 1. All tasks sorted by priority then time ─────────────────────────────────

section("1. ALL TASKS  —  sorted by priority then time")

rows = []
for t in scheduler.sort_by_priority_then_time():
    rows.append([
        priority_badge(t.priority),
        f"{task_emoji(t.title)}  {t.title}",
        f"{t.duration_mins} min",
        t.start_time or "—",
        f"{FREQ_ICON.get(t.frequency, '')} {t.frequency or '—'}".strip(),
        t.pet_name or "—",
    ])

print(tabulate(
    rows,
    headers=["Priority", "Task", "Duration", "Start", "Repeats", "Pet"],
    tablefmt="rounded_outline",
))

# ── 2. Conflict detection ─────────────────────────────────────────────────────

section("2. CONFLICT DETECTION")

conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  ⚠️  {warning}")
else:
    print("  ✅  No scheduling conflicts found.")

# ── 3. Recurring tasks ────────────────────────────────────────────────────────

section("3. RECURRING TASKS")

feeding  = next(t for t in scheduler.tasks if t.title == "Feeding")
grooming = next(t for t in scheduler.tasks if t.title == "Grooming")

next_feeding  = scheduler.mark_task_complete(feeding)
next_grooming = scheduler.mark_task_complete(grooming)

recur_rows = [
    [f"🍽️  {feeding.title}",  STATUS_ICON[feeding.completed],  feeding.frequency,  "Next instance added ✅"],
    [f"✂️  {grooming.title}", STATUS_ICON[grooming.completed], grooming.frequency, "Next instance added ✅"],
]
print(tabulate(
    recur_rows,
    headers=["Task", "Done", "Frequency", "Result"],
    tablefmt="rounded_outline",
))

# ── 4. Filter by status ───────────────────────────────────────────────────────

section("4. FILTER BY STATUS")

done    = scheduler.filter_tasks(completed=True)
pending = scheduler.filter_tasks(completed=False)

status_rows = [
    ["✅  Completed", len(done),    ", ".join(t.title for t in done)    or "—"],
    ["⬜  Pending",   len(pending), ", ".join(t.title for t in pending) or "—"],
]
print(tabulate(status_rows, headers=["Status", "Count", "Tasks"], tablefmt="rounded_outline"))

# ── 5. Filter by pet ──────────────────────────────────────────────────────────

section("5. FILTER BY PET")

pet_rows = []
for pet, icon in [(pet1, SPECIES_ICON["dog"]), (pet2, SPECIES_ICON["cat"])]:
    tasks = scheduler.filter_tasks(pet_name=pet.name)
    pet_rows.append([
        f"{icon}  {pet.name}",
        len(tasks),
        ", ".join(t.title for t in tasks) or "—",
    ])
print(tabulate(pet_rows, headers=["Pet", "Tasks", "Task titles"], tablefmt="rounded_outline"))

# ── 6. Suggest next free slot ─────────────────────────────────────────────────

section("6. NEXT AVAILABLE SLOT")

for duration in [15, 30, 60]:
    slot = scheduler.suggest_next_slot(duration, search_from="06:00")
    if slot:
        print(f"  🕐  Next free {duration}-min slot : {slot}")
    else:
        print(f"  ❌  No {duration}-min slot available today")

# ── 7. Today's schedule (priority plan) ──────────────────────────────────────

section("7. TODAY'S SCHEDULE  —  priority-based plan")

plan = scheduler.build_plan()
scheduled_set = {id(t) for t in plan.scheduled}

sched_rows = []
for t in scheduler.sort_by_priority_then_time():
    if id(t) in scheduled_set:
        sched_rows.append([
            priority_badge(t.priority),
            f"{task_emoji(t.title)}  {t.title}",
            f"{t.duration_mins} min",
            t.start_time or "—",
        ])

print(tabulate(
    sched_rows,
    headers=["Priority", "Task", "Duration", "Start"],
    tablefmt="rounded_outline",
))

total = sum(t.duration_mins for t in plan.scheduled)
print(f"\n  ⏱  Time used : {total} / {owner.available_mins} min")

if plan.skipped:
    print(f"\n  Skipped ({len(plan.skipped)}) — not enough time:")
    for t in plan.skipped:
        print(f"    {PRIORITY_ICON.get(t.priority, '⚪')} {task_emoji(t.title)}  {t.title}  ({t.duration_mins} min)")

print()
print("=" * 62)
print("  🐾  End of PawPal+ daily report")
print("=" * 62)
print()
