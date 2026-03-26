from __future__ import annotations
from dataclasses import dataclass, field


PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3}


@dataclass
class Owner:
    """Represents the pet owner and their total available time for the day."""

    name: str
    available_mins: int  # total minutes available in the day


@dataclass
class Pet:
    """Represents a pet with basic identifying information."""

    name: str
    species: str
    age: int  # in years


@dataclass
class CareTask:
    """A single pet care task with duration, priority, scheduling time, and recurrence."""

    title: str
    duration_mins: int
    priority: str           # "low" | "medium" | "high"
    preferred_time: str | None = None   # "morning" | "afternoon" | "evening" | None
    start_time: str | None = None       # "HH:MM" 24-hour format
    completed: bool = False
    frequency: str | None = None        # "daily" | "weekly" | None
    pet_name: str | None = None         # used for cross-pet filtering

    def priority_value(self) -> int:
        """Return numeric priority so tasks can be sorted (higher = more important)."""
        return PRIORITY_MAP.get(self.priority, 0)


@dataclass
class DailyPlan:
    """The output of a scheduling run: tasks that fit and tasks that were skipped."""

    scheduled: list[CareTask] = field(default_factory=list)
    skipped: list[CareTask] = field(default_factory=list)

    def explain(self) -> str:
        """Return a plain-English summary of what was scheduled and why."""
        lines = []

        if self.scheduled:
            lines.append("**Scheduled tasks:**")
            for task in self.scheduled:
                reason = f"priority: {task.priority}"
                lines.append(f"- {task.title} ({task.duration_mins} min) — {reason}")
        else:
            lines.append("No tasks could be scheduled.")

        if self.skipped:
            lines.append("\n**Skipped tasks (not enough time):**")
            for task in self.skipped:
                lines.append(f"- {task.title} ({task.duration_mins} min, priority: {task.priority})")

        total = sum(t.duration_mins for t in self.scheduled)
        lines.append(f"\nTotal time planned: {total} min")

        return "\n".join(lines)


@dataclass
class Scheduler:
    """Builds a daily care plan by fitting tasks into the owner's available time by priority."""

    owner: Owner
    pet: Pet
    tasks: list[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        """Add a CareTask to the task list."""
        self.tasks.append(task)

    def build_plan(self) -> DailyPlan:
        """Sort tasks by priority, fit them into available time, return a DailyPlan."""
        # Sort highest priority first; preserve insertion order for ties (stable sort)
        sorted_tasks = sorted(self.tasks, key=lambda t: t.priority_value(), reverse=True)

        plan = DailyPlan()
        time_remaining = self.owner.available_mins

        for task in sorted_tasks:
            if task.duration_mins <= time_remaining:
                plan.scheduled.append(task)
                time_remaining -= task.duration_mins
            else:
                plan.skipped.append(task)

        return plan

    def sort_by_time(self) -> list[CareTask]:
        """Return tasks sorted by start_time (HH:MM); tasks with no time go last."""
        timed = sorted(
            (t for t in self.tasks if t.start_time),
            key=lambda t: t.start_time  # HH:MM strings sort correctly lexicographically
        )
        untimed = [t for t in self.tasks if not t.start_time]
        return timed + untimed

    def filter_tasks(
        self,
        *,
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list[CareTask]:
        """Return tasks matching the given completion status and/or pet name."""
        result = self.tasks
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if pet_name is not None:
            result = [t for t in result if t.pet_name == pet_name]
        return result

    def mark_task_complete(self, task: CareTask) -> CareTask | None:
        """Mark a task done; if it recurs daily or weekly, add the next instance and return it."""
        task.completed = True
        if task.frequency in ("daily", "weekly"):
            next_task = CareTask(
                title=task.title,
                duration_mins=task.duration_mins,
                priority=task.priority,
                preferred_time=task.preferred_time,
                start_time=task.start_time,
                frequency=task.frequency,
                pet_name=task.pet_name,
            )
            self.tasks.append(next_task)
            return next_task
        return None

    def detect_conflicts(self) -> list[str]:
        """Return warning messages for any two tasks sharing the same start_time."""
        warnings = []
        seen: dict[str, CareTask] = {}
        for task in (t for t in self.tasks if t.start_time):
            if task.start_time in seen:
                other = seen[task.start_time]
                warnings.append(
                    f"WARNING: Conflict at {task.start_time} — "
                    f"'{task.title}' and '{other.title}' are scheduled at the same time."
                )
            else:
                seen[task.start_time] = task
        return warnings
