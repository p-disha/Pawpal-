import pytest
from pawpal import Owner, Pet, CareTask, Scheduler, DailyPlan


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
