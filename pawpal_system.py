from __future__ import annotations
from dataclasses import dataclass, field
import json
import pathlib


PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3}


@dataclass
class Owner:
    """Represents the pet owner and their total available time for the day."""

    name: str
    available_mins: int  # total minutes available in the day

    def to_dict(self) -> dict:
        """Serialize to a JSON-compatible dictionary."""
        return {"name": self.name, "available_mins": self.available_mins}

    @classmethod
    def from_dict(cls, data: dict) -> Owner:
        """Reconstruct an Owner from a dictionary."""
        return cls(name=data["name"], available_mins=data["available_mins"])


@dataclass
class Pet:
    """Represents a pet with basic identifying information."""

    name: str
    species: str
    age: int  # in years

    def to_dict(self) -> dict:
        """Serialize to a JSON-compatible dictionary."""
        return {"name": self.name, "species": self.species, "age": self.age}

    @classmethod
    def from_dict(cls, data: dict) -> Pet:
        """Reconstruct a Pet from a dictionary."""
        return cls(name=data["name"], species=data["species"], age=data["age"])


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

    def to_dict(self) -> dict:
        """Serialize to a JSON-compatible dictionary."""
        return {
            "title": self.title,
            "duration_mins": self.duration_mins,
            "priority": self.priority,
            "preferred_time": self.preferred_time,
            "start_time": self.start_time,
            "completed": self.completed,
            "frequency": self.frequency,
            "pet_name": self.pet_name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> CareTask:
        """Reconstruct a CareTask from a dictionary."""
        return cls(
            title=data["title"],
            duration_mins=data["duration_mins"],
            priority=data["priority"],
            preferred_time=data.get("preferred_time"),
            start_time=data.get("start_time"),
            completed=data.get("completed", False),
            frequency=data.get("frequency"),
            pet_name=data.get("pet_name"),
        )


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

    def build_plan_weighted(self) -> DailyPlan:
        """Schedule tasks by value density (priority per minute) to fit more high-value work.

        Each task is scored as priority_value * 100 / duration_mins.
        A high-priority 10-min task outscores a high-priority 60-min task, so the
        algorithm packs more valuable tasks into the available time budget than the
        basic greedy approach can when large high-priority tasks would otherwise
        crowd out several smaller high-value ones.
        """
        def value_density(task: CareTask) -> float:
            return task.priority_value() * 100 / task.duration_mins

        ranked = sorted(self.tasks, key=value_density, reverse=True)

        plan = DailyPlan()
        time_remaining = self.owner.available_mins

        for task in ranked:
            if task.duration_mins <= time_remaining:
                plan.scheduled.append(task)
                time_remaining -= task.duration_mins
            else:
                plan.skipped.append(task)

        return plan

    def suggest_next_slot(self, duration_mins: int, search_from: str = "06:00") -> str | None:
        """Return the earliest HH:MM slot that fits a task of the given duration.

        Scans timed tasks in chronological order and finds the first gap large enough
        to fit duration_mins minutes, starting from search_from. Returns None if no
        gap exists before 22:00 (end of day).
        """
        def to_mins(t: str) -> int:
            h, m = t.split(":")
            return int(h) * 60 + int(m)

        def to_hhmm(mins: int) -> str:
            return f"{mins // 60:02d}:{mins % 60:02d}"

        end_of_day = to_mins("22:00")
        cursor = to_mins(search_from)

        occupied = sorted(
            [(to_mins(t.start_time), to_mins(t.start_time) + t.duration_mins)
             for t in self.tasks if t.start_time],
            key=lambda x: x[0],
        )

        for start, end in occupied:
            if start >= cursor + duration_mins:
                return to_hhmm(cursor)   # gap before this task is big enough
            if end > cursor:
                cursor = end             # skip past this task

        if cursor + duration_mins <= end_of_day:
            return to_hhmm(cursor)

        return None


# ── Persistence ───────────────────────────────────────────────────────────────

def save_to_json(
    owner: Owner,
    pet: Pet,
    tasks: list[CareTask],
    path: str = "data.json",
) -> None:
    """Serialize owner, pet, and tasks to a JSON file."""
    payload = {
        "owner": owner.to_dict(),
        "pet": pet.to_dict(),
        "tasks": [t.to_dict() for t in tasks],
    }
    pathlib.Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_from_json(path: str = "data.json") -> tuple[Owner, Pet, list[CareTask]]:
    """Load owner, pet, and tasks from a JSON file.

    Returns a tuple of (Owner, Pet, list[CareTask]).
    Raises FileNotFoundError if the file does not exist.
    """
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    owner = Owner.from_dict(data["owner"])
    pet   = Pet.from_dict(data["pet"])
    tasks = [CareTask.from_dict(t) for t in data.get("tasks", [])]
    return owner, pet, tasks
