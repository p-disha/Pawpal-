# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

+------------------+         +------------------+
|      Owner       |         |       Pet        |
+------------------+         +------------------+
| name: str        |1      1 | name: str        |
| available_mins:  |-------->| species: str     |
|   int            |         | age: int         |
+------------------+         +------------------+

+------------------+
|    CareTask      |
+------------------+
| title: str       |
| duration_mins:   |
|   int            |
| priority: str    |  ("low" | "medium" | "high")
| preferred_time:  |
|   str | None     |  ("morning" | "afternoon" | "evening")
+------------------+
| priority_value() |  → int  (maps "high"→3, "medium"→2, "low"→1)
+------------------+

+------------------+
|    Scheduler     |
+------------------+
| owner: Owner     |
| pet: Pet         |
| tasks: list[CareTask] |
+------------------+
| add_task(task)   |
| build_plan()     |  → DailyPlan
+------------------+

+------------------+
|   DailyPlan      |
+------------------+
| scheduled: list[CareTask]  |
| skipped:   list[CareTask]  |
+------------------+
| explain() → str  |  narrative of what was chosen and why
+------------------+

- What classes did you include, and what responsibilities did you assign to each?

4 classes:

Owner — holds the owner's name and how many minutes they have available in a day. Represents the constraint side of scheduling.

Pet — holds the pet's name, species, and age. Provides context for why certain tasks exist.

CareTask — represents a single task with a title, duration, priority, and optional preferred time of day. Has a priority_value() helper that converts "low"/"medium"/"high" to a number so tasks can be ranked.

Scheduler — the core logic class. Owns an Owner, a Pet, and a list of CareTasks. add_task() lets you register tasks; build_plan() sorts by priority, fits tasks into the owner's available time, and returns a DailyPlan.

DailyPlan — the output of scheduling. Holds two lists: tasks that made it in (scheduled) and tasks that were dropped (skipped). Has an explain() method that produces a plain-English summary of what was planned and why.

Core responsibility split: Scheduler decides what fits; DailyPlan records what was decided and explains it. CareTask knows its own priority weight but nothing about time budgets.

**b. Design changes**

- Did your design change during implementation?
yes
- If yes, describe at least one change and why you made it.

+-------------------------+          +-------------------------+
|         Owner           |          |          Pet            |
+-------------------------+          +-------------------------+
| + name: str             |          | + name: str             |
| + available_mins: int   |          | + species: str          |
+-------------------------+          | + age: int              |
                                     +-------------------------+

+------------------------------------+
|            CareTask                |
+------------------------------------+
| + title: str                       |
| + duration_mins: int               |
| + priority: str                    |
| + preferred_time: str | None       |
+------------------------------------+
| + priority_value() → int           |
+------------------------------------+

+------------------------------------+
|            Scheduler               |
+------------------------------------+
| + owner: Owner                     |
| + pet: Pet                         |
| + tasks: list[CareTask]            |
+------------------------------------+
| + add_task(task: CareTask) → None  |
| + build_plan() → DailyPlan         |
+------------------------------------+
         |                   |
         | uses              | creates
         v                   v
+------+                +----------------------------+
| Owner|                |         DailyPlan          |
| Pet  |                +----------------------------+
+------+                | + scheduled: list[CareTask]|
                        | + skipped: list[CareTask]  |
                        +----------------------------+
                        | + explain() → str          |
                        +----------------------------+


---

Initial design
Owner had no age/extra fields	
What was actually built Stayed minimal — just name + available_mins
Initial design
Pet was loosely defined	
What was actually built Added age: int (used in UI)
Initial design
preferred_time was planned	
What was actually built Stored on CareTask but not yet used by scheduler
Initial design
Scheduler had no detail	
What was actually built Greedy priority-first algorithm with stable tie-breaking
Initial design
DailyPlan.explain() was vague	
What was actually built Returns markdown-formatted string with scheduled, skipped, and total time
Initial design
Owner ↔ Pet were linked 1-to-1	
What was actually built In practice, Scheduler holds them independently (no direct owner→pet reference)

One honest gap to note: preferred_time is stored on CareTask and shown in the UI, but build_plan() doesn't use it yet — the scheduler only considers priority and duration. That's a natural next feature to add.

In Phase 2, four more fields were added to `CareTask` (`start_time`, `completed`, `frequency`, `pet_name`) and four new methods to `Scheduler` (`sort_by_time`, `filter_tasks`, `mark_task_complete`, `detect_conflicts`). These were not in the initial UML and emerged from the feature requirements rather than upfront design. The final UML (`uml_final.png`) reflects all of these additions.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers two constraints: total time available (owner's available_mins) and task priority (high/medium/low). Preferred time of day is stored on each task but not yet enforced by the scheduler — it is captured for a future iteration.

Time availability was treated as the hard constraint because exceeding it makes the plan physically impossible. Priority was the soft ranking signal: when time runs out, lower-priority tasks are dropped first. Preferred time was intentionally deferred — it adds complexity (time-slot splitting, conflict resolution) that wasn't necessary to deliver a useful first version.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler uses a greedy algorithm: it sorts all tasks by priority (highest first) and fits them in one pass, skipping any task that doesn't fit in the remaining time. This means a large high-priority task can consume most of the budget and cause several smaller lower-priority tasks to be skipped, even if a different ordering could have fit more tasks overall.

This tradeoff is reasonable for pet care because the owner has already expressed which tasks matter most. Missing a low-priority grooming session is a better outcome than missing medications or a walk. Simplicity also matters here — a greedy plan is easy to explain and easy for an owner to review and override manually.

A second tradeoff exists in conflict detection: `detect_conflicts()` only flags tasks that share an exact `start_time` string match ("08:00" == "08:00"). It does not check for duration-based overlaps — a 30-minute task at 08:00 and a 10-minute task at 08:15 would not be flagged even though they overlap in real time. This is a deliberate simplification: exact-match detection is O(n) with a single dictionary pass, requires no date arithmetic, and catches the most common mistake (copying the same time slot). Overlap detection would require converting times to integers and comparing ranges, adding complexity that isn't necessary for an MVP planning tool where the owner reviews the final schedule anyway.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

AI was used across every phase: drafting the initial UML, converting it to Python stubs, implementing scheduling logic incrementally, writing tests, and wiring up the Streamlit UI. The most useful prompts were step-scoped and concrete — for example, "implement scheduling logic in small increments" produced focused, reviewable changes rather than one large dump of code. Following the README's suggested workflow as a prompt structure kept the AI aligned with the intended learning sequence.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

The AI's initial UML showed a direct 1-to-1 ownership arrow from Owner to Pet. During implementation it became clear that Scheduler holds both independently — there is no meaningful reason for an Owner object to carry a Pet reference in the current design. The relationship was removed from the refined UML. Verification was done by reading the actual dataclass definitions and asking whether any code ever accessed owner.pet — it didn't, so the association was dropped as an inaccurate diagram artifact.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

55 tests across all classes and methods, organised in 10 groups:

- **CareTask attributes** — all 8 fields tested individually (defaults and stored values), including the Phase 2 additions: `start_time`, `completed`, `frequency`, `pet_name`.
- **priority_value()** — all three valid priorities plus unknown input returning 0.
- **Scheduler.add_task()** — single and multiple tasks appended correctly.
- **Scheduler.build_plan()** — tasks fit, skipped when over budget, priority wins tie-break, empty plan, exact-fit boundary, idempotency, equal-priority insertion order, and documented behaviour that completed tasks are not filtered out of the plan.
- **Scheduler.sort_by_time()** — chronological ordering, untimed tasks last, all-untimed, all-timed, empty list.
- **Scheduler.filter_tasks()** — by completion status, pet name, combined, no-args returns all, no match returns empty.
- **Scheduler.mark_task_complete()** — flag set, daily recurrence, weekly recurrence, non-recurring returns None, all attributes preserved on copy.
- **Scheduler.detect_conflicts()** — same-time flagged, no overlap, multiple clashes, single task (no conflict), three tasks at one slot (two warnings), untimed tasks ignored, warning contains task titles.
- **DailyPlan.explain()** — scheduled listed, skipped listed, no-tasks message, total time, zero total, priority shown, all-skipped scenario.

These tests mattered because the scheduler's correctness is not visually obvious — a bug in priority sorting or time accounting could produce a plan that looks plausible in the UI but is wrong. Tests make the logic verifiable independent of the UI, and they document intended behaviour (like `build_plan` including completed tasks) that would otherwise be invisible.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

Confidence is high — 55 tests pass covering normal cases, boundary conditions, and edge cases for every method in `pawpal_system.py`. The main remaining gap is that `build_plan()` does not filter out already-completed tasks; a test was added to document this current behaviour, but fixing it would require a decision about whether completed recurring tasks should be excluded or replaced. Other gaps worth addressing: duration-based overlap detection (two tasks whose windows overlap even if start times differ), very large task lists for performance, and end-to-end UI testing via Streamlit's testing utilities.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The clean separation of responsibilities across classes worked well in practice. Scheduler deciding what fits, DailyPlan recording and explaining the result, and CareTask knowing only its own priority weight meant each piece could be implemented and tested independently. The test suite in particular benefited from this — each class could be instantiated in isolation without needing to set up the entire system.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

The most obvious improvement is implementing preferred_time in build_plan(). This would require dividing the day into time slots (morning, afternoon, evening) and assigning tasks to slots based on preference while still respecting the priority and duration constraints. A secondary improvement would be letting the owner specify a start time and having the plan output actual clock times (e.g., "9:00 AM — Morning walk, 20 min") rather than just an ordered list.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Designing before building — even a rough UML draft — made AI collaboration significantly more productive. When the structure was agreed on upfront, AI-generated code fit together without major restructuring. The moments where friction occurred (like the Owner→Pet relationship) were exactly the places where the design hadn't been thought through carefully. The takeaway is that AI accelerates execution, but the designer still needs to own the structure: AI will fill in what you specify, including your mistakes.
