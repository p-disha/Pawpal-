from pawpal_system import Owner, Pet, CareTask, Scheduler

owner = Owner(name="Jordan", available_mins=90)
pet1  = Pet(name="Mochi", species="dog", age=3)
pet2  = Pet(name="Luna",  species="cat", age=5)

scheduler = Scheduler(owner=owner, pet=pet1)

# Tasks added OUT OF ORDER intentionally to test sort_by_time
scheduler.add_task(CareTask("Evening walk",    duration_mins=30, priority="medium", start_time="18:00", pet_name="Mochi"))
scheduler.add_task(CareTask("Feeding",         duration_mins=10, priority="high",   start_time="07:30", pet_name="Mochi", frequency="daily"))
scheduler.add_task(CareTask("Grooming",        duration_mins=20, priority="medium", start_time="14:00", pet_name="Mochi", frequency="weekly"))
scheduler.add_task(CareTask("Morning walk",    duration_mins=30, priority="high",   start_time="08:00", pet_name="Mochi"))
scheduler.add_task(CareTask("Litter box",      duration_mins=10, priority="medium", start_time="08:00", pet_name="Luna"))  # conflict with Morning walk
scheduler.add_task(CareTask("Laser play",      duration_mins=15, priority="low",    start_time="19:00", pet_name="Luna"))
scheduler.add_task(CareTask("Enrichment play", duration_mins=40, priority="low",    pet_name="Mochi"))  # no start_time

# ── 1. Sort by time ──────────────────────────────────────────────────────────
print("=" * 55)
print("  1. TASKS SORTED BY TIME")
print("=" * 55)
for t in scheduler.sort_by_time():
    time_label = t.start_time if t.start_time else "no time set"
    print(f"  [{time_label}]  {t.title} ({t.duration_mins} min, {t.priority})")

# ── 2. Conflict detection ─────────────────────────────────────────────────────
print("\n" + "=" * 55)
print("  2. CONFLICT DETECTION")
print("=" * 55)
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  {warning}")
else:
    print("  No conflicts found.")

# ── 3. Recurring task demo ────────────────────────────────────────────────────
print("\n" + "=" * 55)
print("  3. RECURRING TASKS")
print("=" * 55)
feeding = next(t for t in scheduler.tasks if t.title == "Feeding")
grooming = next(t for t in scheduler.tasks if t.title == "Grooming")

next_feeding  = scheduler.mark_task_complete(feeding)
next_grooming = scheduler.mark_task_complete(grooming)

print(f"  Marked '{feeding.title}' complete (frequency: {feeding.frequency})")
print(f"  -> Next occurrence created: {next_feeding.title} | completed={next_feeding.completed}")

print(f"  Marked '{grooming.title}' complete (frequency: {grooming.frequency})")
print(f"  -> Next occurrence created: {next_grooming.title} | completed={next_grooming.completed}")

# ── 4. Filter by completion status ───────────────────────────────────────────
print("\n" + "=" * 55)
print("  4. FILTER BY STATUS")
print("=" * 55)
done     = scheduler.filter_tasks(completed=True)
pending  = scheduler.filter_tasks(completed=False)
print(f"  Completed tasks ({len(done)}): {[t.title for t in done]}")
print(f"  Pending tasks   ({len(pending)}): {[t.title for t in pending]}")

# ── 5. Filter by pet name ─────────────────────────────────────────────────────
print("\n" + "=" * 55)
print("  5. FILTER BY PET NAME")
print("=" * 55)
mochi_tasks = scheduler.filter_tasks(pet_name="Mochi")
luna_tasks  = scheduler.filter_tasks(pet_name="Luna")
print(f"  Mochi's tasks ({len(mochi_tasks)}): {[t.title for t in mochi_tasks]}")
print(f"  Luna's tasks  ({len(luna_tasks)}):  {[t.title for t in luna_tasks]}")

# ── 6. Daily plan ─────────────────────────────────────────────────────────────
print("\n" + "=" * 55)
print("  6. TODAY'S SCHEDULE (priority-based plan)")
print("=" * 55)
plan = scheduler.build_plan()
print(plan.explain())
print("=" * 55)
