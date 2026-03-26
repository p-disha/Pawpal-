# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## App Screenshots

### Owner, Pet & Task Input
Enter owner name, available time, pet details, and add tasks with duration and priority.

![Task input form](image.png)

### Generated Daily Schedule
The scheduler produces a prioritized plan, skips tasks that don't fit, and explains its reasoning.

![Generated schedule output](image-1.png)

## Running the app

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Run tests
pytest test_pawpal.py -v

# Launch the app
streamlit run app.py
```

## Smarter Scheduling

Beyond basic priority-based planning, the scheduler now supports:

- **Time-based sorting** — `Scheduler.sort_by_time()` orders tasks by their `start_time` (HH:MM format) using a lambda key on lexicographically comparable strings. Tasks with no time set are placed at the end.

- **Filtering** — `Scheduler.filter_tasks(completed=..., pet_name=...)` returns a subset of tasks by completion status, pet name, or both. Useful for showing only pending tasks or isolating one pet's workload.

- **Recurring tasks** — `CareTask` now has a `frequency` field (`"daily"` or `"weekly"`). Calling `Scheduler.mark_task_complete(task)` marks the task done and automatically appends a fresh copy to the task list for the next occurrence.

- **Conflict detection** — `Scheduler.detect_conflicts()` scans all tasks with a `start_time` and returns a warning string for any two tasks sharing the exact same slot. This is an intentional lightweight strategy (O(n) dictionary pass) — it catches duplicate time assignments without the complexity of duration-overlap arithmetic.

## Project structure

```
pawpal_system.py   # Core classes: Owner, Pet, CareTask, Scheduler, DailyPlan
app.py             # Streamlit UI
main.py            # Terminal demo: sorting, filtering, conflicts, recurring tasks
test_pawpal.py     # pytest test suite (25 tests)
reflection.md      # Design decisions and project reflection
requirements.txt
```