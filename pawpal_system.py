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
    """A single pet care task with a duration, priority, and optional time-of-day preference."""

    title: str
    duration_mins: int
    priority: str  # "low" | "medium" | "high"
    preferred_time: str | None = None  # "morning" | "afternoon" | "evening" | None

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
