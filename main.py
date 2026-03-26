from pawpal_system import Owner, Pet, CareTask, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", available_mins=90)

pet1 = Pet(name="Mochi", species="dog", age=3)
pet2 = Pet(name="Luna", species="cat", age=5)

# --- Tasks for Mochi (dog) ---
scheduler_mochi = Scheduler(owner=owner, pet=pet1)
scheduler_mochi.add_task(CareTask("Morning walk",    duration_mins=30, priority="high",   preferred_time="morning"))
scheduler_mochi.add_task(CareTask("Feeding",         duration_mins=10, priority="high",   preferred_time="morning"))
scheduler_mochi.add_task(CareTask("Grooming",        duration_mins=20, priority="medium", preferred_time="afternoon"))
scheduler_mochi.add_task(CareTask("Enrichment play", duration_mins=40, priority="low",    preferred_time="evening"))

# --- Tasks for Luna (cat) ---
scheduler_luna = Scheduler(owner=owner, pet=pet2)
scheduler_luna.add_task(CareTask("Feeding",          duration_mins=10, priority="high",   preferred_time="morning"))
scheduler_luna.add_task(CareTask("Litter box clean", duration_mins=10, priority="medium", preferred_time="morning"))
scheduler_luna.add_task(CareTask("Laser play",       duration_mins=15, priority="low",    preferred_time="evening"))

# --- Build plans ---
plan_mochi = scheduler_mochi.build_plan()
plan_luna  = scheduler_luna.build_plan()

# --- Print schedule ---
print("=" * 50)
print("       TODAY'S SCHEDULE")
print(f"       Owner: {owner.name}  |  Available: {owner.available_mins} min")
print("=" * 50)

print(f"\n--- {pet1.name} ({pet1.species}, age {pet1.age}) ---")
print(plan_mochi.explain())

print(f"\n--- {pet2.name} ({pet2.species}, age {pet2.age}) ---")
print(plan_luna.explain())

print("\n" + "=" * 50)
