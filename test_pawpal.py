import pytest
from pawpal_system import Owner, Pet, CareTask, Scheduler, DailyPlan


# --- Fixtures ---

@pytest.fixture
def owner():
    return Owner(name="Jordan", available_mins=60)

@pytest.fixture
def pet():
    return Pet(name="Mochi", species="dog", age=3)

@pytest.fixture
def scheduler(owner, pet):
    return Scheduler(owner=owner, pet=pet)


# --- Owner ---

def test_owner_stores_name_and_time():
    o = Owner(name="Alex", available_mins=45)
    assert o.name == "Alex"
    assert o.available_mins == 45


# --- Pet ---

def test_pet_stores_attributes():
    p = Pet(name="Luna", species="cat", age=5)
    assert p.name == "Luna"
    assert p.species == "cat"
    assert p.age == 5


# --- CareTask attributes ---

def test_caretask_preferred_time_default_is_none():
    task = CareTask("Walk", 20, "high")
    assert task.preferred_time is None

def test_caretask_preferred_time_stored():
    task = CareTask("Walk", 20, "high", preferred_time="morning")
    assert task.preferred_time == "morning"


# --- CareTask.priority_value ---

def test_priority_value_high():
    task = CareTask("Meds", 10, "high")
    assert task.priority_value() == 3

def test_priority_value_medium():
    task = CareTask("Walk", 20, "medium")
    assert task.priority_value() == 2

def test_priority_value_low():
    task = CareTask("Bath", 30, "low")
    assert task.priority_value() == 1

def test_priority_value_unknown():
    task = CareTask("Nap", 15, "urgent")  # not a valid priority
    assert task.priority_value() == 0


# --- Scheduler.add_task ---

def test_add_task(scheduler):
    task = CareTask("Walk", 20, "high")
    scheduler.add_task(task)
    assert task in scheduler.tasks

def test_add_multiple_tasks(scheduler):
    t1 = CareTask("Walk", 20, "high")
    t2 = CareTask("Feed", 10, "medium")
    scheduler.add_task(t1)
    scheduler.add_task(t2)
    assert len(scheduler.tasks) == 2


# --- Scheduler.build_plan: scheduling ---

def test_all_tasks_fit(scheduler):
    scheduler.add_task(CareTask("Walk", 20, "high"))
    scheduler.add_task(CareTask("Feed", 10, "medium"))
    plan = scheduler.build_plan()
    assert len(plan.scheduled) == 2
    assert len(plan.skipped) == 0

def test_task_skipped_when_no_time(scheduler):
    # 60 min available; add tasks totalling 70 min
    scheduler.add_task(CareTask("Walk", 30, "high"))
    scheduler.add_task(CareTask("Feed", 20, "medium"))
    scheduler.add_task(CareTask("Bath", 30, "low"))  # should be skipped
    plan = scheduler.build_plan()
    titles_scheduled = [t.title for t in plan.scheduled]
    titles_skipped = [t.title for t in plan.skipped]
    assert "Bath" in titles_skipped
    assert "Walk" in titles_scheduled
    assert "Feed" in titles_scheduled

def test_high_priority_scheduled_over_low(scheduler):
    # Only 20 min available; two tasks compete
    scheduler.owner.available_mins = 20
    scheduler.add_task(CareTask("Bath", 20, "low"))
    scheduler.add_task(CareTask("Meds", 20, "high"))
    plan = scheduler.build_plan()
    assert plan.scheduled[0].title == "Meds"
    assert any(t.title == "Bath" for t in plan.skipped)

def test_no_tasks_returns_empty_plan(scheduler):
    plan = scheduler.build_plan()
    assert plan.scheduled == []
    assert plan.skipped == []

def test_single_task_larger_than_budget_is_skipped(scheduler):
    scheduler.owner.available_mins = 10
    scheduler.add_task(CareTask("Long walk", 60, "high"))
    plan = scheduler.build_plan()
    assert len(plan.scheduled) == 0
    assert len(plan.skipped) == 1

def test_task_fits_exactly_into_remaining_budget(scheduler):
    # Task duration == available_mins exactly; should be scheduled, not skipped
    scheduler.owner.available_mins = 25
    scheduler.add_task(CareTask("Exact fit", 25, "high"))
    plan = scheduler.build_plan()
    assert len(plan.scheduled) == 1
    assert len(plan.skipped) == 0

def test_build_plan_twice_gives_same_result(scheduler):
    scheduler.add_task(CareTask("Walk", 30, "high"))
    scheduler.add_task(CareTask("Feed", 10, "medium"))
    plan1 = scheduler.build_plan()
    plan2 = scheduler.build_plan()
    assert [t.title for t in plan1.scheduled] == [t.title for t in plan2.scheduled]
    assert [t.title for t in plan1.skipped] == [t.title for t in plan2.skipped]

def test_equal_priority_preserves_insertion_order(scheduler):
    t1 = CareTask("Feed", 10, "medium")
    t2 = CareTask("Brush", 10, "medium")
    scheduler.add_task(t1)
    scheduler.add_task(t2)
    plan = scheduler.build_plan()
    assert plan.scheduled[0].title == "Feed"
    assert plan.scheduled[1].title == "Brush"


# --- DailyPlan.explain ---

def test_explain_lists_scheduled_tasks():
    plan = DailyPlan(
        scheduled=[CareTask("Walk", 20, "high")],
        skipped=[]
    )
    text = plan.explain()
    assert "Walk" in text
    assert "20 min" in text

def test_explain_lists_skipped_tasks():
    plan = DailyPlan(
        scheduled=[CareTask("Feed", 10, "high")],
        skipped=[CareTask("Bath", 30, "low")]
    )
    text = plan.explain()
    assert "Bath" in text
    assert "Skipped" in text

def test_explain_no_tasks_message():
    plan = DailyPlan()
    text = plan.explain()
    assert "No tasks could be scheduled" in text

def test_explain_shows_total_time():
    plan = DailyPlan(
        scheduled=[CareTask("Walk", 20, "high"), CareTask("Feed", 10, "medium")],
        skipped=[]
    )
    text = plan.explain()
    assert "30 min" in text

def test_explain_shows_zero_total_when_nothing_scheduled():
    plan = DailyPlan(skipped=[CareTask("Bath", 30, "low")])
    text = plan.explain()
    assert "0 min" in text

def test_explain_shows_priority_in_scheduled_output():
    plan = DailyPlan(scheduled=[CareTask("Meds", 10, "high")])
    text = plan.explain()
    assert "high" in text

def test_explain_all_skipped_no_scheduled():
    plan = DailyPlan(
        scheduled=[],
        skipped=[CareTask("Walk", 60, "medium")]
    )
    text = plan.explain()
    assert "No tasks could be scheduled" in text
    assert "Walk" in text


# --- Scheduler.sort_by_time ---

def test_sort_by_time_chronological_order(scheduler):
    scheduler.add_task(CareTask("Evening walk", 30, "medium", start_time="18:00"))
    scheduler.add_task(CareTask("Feeding",      10, "high",   start_time="07:30"))
    scheduler.add_task(CareTask("Grooming",     20, "medium", start_time="14:00"))
    result = scheduler.sort_by_time()
    times = [t.start_time for t in result]
    assert times == ["07:30", "14:00", "18:00"]

def test_sort_by_time_untimed_tasks_go_last(scheduler):
    scheduler.add_task(CareTask("Walk",  30, "high",   start_time="08:00"))
    scheduler.add_task(CareTask("Bath",  20, "medium"))           # no start_time
    scheduler.add_task(CareTask("Meds",  10, "high",   start_time="07:00"))
    result = scheduler.sort_by_time()
    assert result[-1].title == "Bath"
    assert result[0].start_time == "07:00"

def test_sort_by_time_all_untimed(scheduler):
    scheduler.add_task(CareTask("Feed",  10, "high"))
    scheduler.add_task(CareTask("Brush", 10, "low"))
    result = scheduler.sort_by_time()
    # Order among untimed tasks preserved (insertion order)
    assert [t.title for t in result] == ["Feed", "Brush"]

def test_sort_by_time_no_tasks(scheduler):
    assert scheduler.sort_by_time() == []


# --- Scheduler.filter_tasks ---

def test_filter_by_completed_false(scheduler):
    t1 = CareTask("Walk", 30, "high")
    t2 = CareTask("Meds", 10, "high", completed=True)  # type: ignore[call-arg]
    scheduler.add_task(t1)
    scheduler.add_task(t2)
    result = scheduler.filter_tasks(completed=False)
    assert all(not t.completed for t in result)
    assert len(result) == 1

def test_filter_by_completed_true(scheduler):
    t1 = CareTask("Walk", 30, "high")
    t2 = CareTask("Meds", 10, "high")
    scheduler.add_task(t1)
    scheduler.add_task(t2)
    scheduler.mark_task_complete(t1)
    result = scheduler.filter_tasks(completed=True)
    assert result == [t1]

def test_filter_by_pet_name(scheduler):
    scheduler.add_task(CareTask("Walk",     30, "high",   pet_name="Mochi"))
    scheduler.add_task(CareTask("Litter",   10, "medium", pet_name="Luna"))
    scheduler.add_task(CareTask("Feeding",  10, "high",   pet_name="Mochi"))
    result = scheduler.filter_tasks(pet_name="Mochi")
    assert all(t.pet_name == "Mochi" for t in result)
    assert len(result) == 2

def test_filter_combined_pet_and_status(scheduler):
    scheduler.add_task(CareTask("Walk",    30, "high",   pet_name="Mochi"))
    scheduler.add_task(CareTask("Feeding", 10, "high",   pet_name="Mochi"))
    scheduler.add_task(CareTask("Litter",  10, "medium", pet_name="Luna"))
    scheduler.mark_task_complete(scheduler.tasks[0])   # complete Walk
    result = scheduler.filter_tasks(completed=False, pet_name="Mochi")
    assert len(result) == 1
    assert result[0].title == "Feeding"

def test_filter_no_match_returns_empty(scheduler):
    scheduler.add_task(CareTask("Walk", 30, "high", pet_name="Mochi"))
    assert scheduler.filter_tasks(pet_name="Bunny") == []


# --- Scheduler.mark_task_complete / recurrence ---

def test_mark_task_complete_sets_flag(scheduler):
    task = CareTask("Walk", 30, "high")
    scheduler.add_task(task)
    scheduler.mark_task_complete(task)
    assert task.completed is True

def test_daily_task_creates_new_instance(scheduler):
    task = CareTask("Feeding", 10, "high", frequency="daily")
    scheduler.add_task(task)
    next_task = scheduler.mark_task_complete(task)
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.frequency == "daily"
    assert next_task.title == "Feeding"
    assert next_task in scheduler.tasks

def test_weekly_task_creates_new_instance(scheduler):
    task = CareTask("Grooming", 20, "medium", frequency="weekly")
    scheduler.add_task(task)
    next_task = scheduler.mark_task_complete(task)
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.frequency == "weekly"

def test_non_recurring_task_returns_none(scheduler):
    task = CareTask("Bath", 30, "low")  # no frequency
    scheduler.add_task(task)
    result = scheduler.mark_task_complete(task)
    assert result is None

def test_recurrence_preserves_task_attributes(scheduler):
    task = CareTask("Meds", 10, "high", start_time="08:00",
                    preferred_time="morning", frequency="daily", pet_name="Mochi")
    scheduler.add_task(task)
    next_task = scheduler.mark_task_complete(task)
    assert next_task.start_time == "08:00"
    assert next_task.preferred_time == "morning"
    assert next_task.pet_name == "Mochi"


# --- Scheduler.detect_conflicts ---

def test_detect_conflicts_same_time(scheduler):
    scheduler.add_task(CareTask("Walk",   30, "high",   start_time="08:00"))
    scheduler.add_task(CareTask("Litter", 10, "medium", start_time="08:00"))
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "08:00" in warnings[0]

def test_detect_conflicts_no_overlap(scheduler):
    scheduler.add_task(CareTask("Walk",    30, "high",   start_time="08:00"))
    scheduler.add_task(CareTask("Feeding", 10, "high",   start_time="09:00"))
    assert scheduler.detect_conflicts() == []

def test_detect_conflicts_multiple_clashes(scheduler):
    scheduler.add_task(CareTask("Walk",     30, "high",   start_time="08:00"))
    scheduler.add_task(CareTask("Litter",   10, "medium", start_time="08:00"))
    scheduler.add_task(CareTask("Feeding",  10, "high",   start_time="12:00"))
    scheduler.add_task(CareTask("Grooming", 20, "medium", start_time="12:00"))
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 2

def test_detect_conflicts_ignores_untimed_tasks(scheduler):
    scheduler.add_task(CareTask("Walk",  30, "high"))   # no start_time
    scheduler.add_task(CareTask("Bath",  20, "medium")) # no start_time
    assert scheduler.detect_conflicts() == []

def test_detect_conflicts_warning_contains_task_titles(scheduler):
    scheduler.add_task(CareTask("Morning walk", 30, "high",   start_time="08:00"))
    scheduler.add_task(CareTask("Litter box",   10, "medium", start_time="08:00"))
    warning = scheduler.detect_conflicts()[0]
    assert "Morning walk" in warning or "Litter box" in warning
