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

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Today's Schedule (2026-10-18) for Alex
------------------------------------------------------------
07:30-08:00  Rex      walk       priority 5
                   note: Use the red leash
08:00-08:15  Rex      feeding    priority 5
                   note: Half cup of kibble
12:00-12:05  Miso     medication priority 5
                   note: Give with a treat
18:00-18:20  Miso     grooming   priority 2
------------------------------------------------------------
```

## Implementation Summary

* The app is built around 4 major classes: PetOwner, Pet, Task, and PlanSchedule. Each holds specific details about the client, pet, daily task, and daily plan. The classes are related the way real-world pet care is: creating an owner, adding pets, and adding tasks builds the ownership tree. PlanSchedule holds a collection of tasks for one day and rejects any task whose time overlaps one already in the plan. Priority (1–5) is stored on each task and shown in the schedule, but PlanSchedule does not yet use it to order or select tasks.

## 🧪 Testing PawPal+

```python -m pytest```

Sample test output:

Output:
```
============================================================================ test session starts ============================================================================
platform win32 -- Python 3.12.1, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\CodePath\Week3\ai110-module2show-pawpal-starter\tests
plugins: anyio-4.15.1
collected 32 items                                                                                                                                                           

test_pawpal.py ................................                                                                                                                        [100%]

============================================================================ 32 passed in 0.07s =============================================================================
```

## 📐 Smarter Scheduling

All scheduling logic lives in `pawpal_system.py`. Methods are on `PlanSchedule` unless marked `Task`.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `PlanSchedule.sort_by_time()`; kept sorted on every change by `_rebuild()` | Sorts tasks by start hour, then start minute. The plan is always in time order, so callers can iterate `arrayOfTasks` directly. |
| Filtering | `PlanSchedule.filter_tasks(status=None, pet_name=None, pets=())` | Takes three optional arguments: a status (`pending`, `incomplete`, or `complete`), a pet name (matched case-insensitively), and `pets`, the owner's list of `Pet` objects used to look up the name. Pass `None` to skip a filter. Results keep time order. |
| Conflict handling | `PlanSchedule.addTasks()` → `_rebuild()`; `_overlaps()` (module-level); `PlanSchedule.tryAddTask()` | Any two tasks whose times overlap are a conflict, whether they belong to the same pet or different pets, because the owner can only do one thing at a time. When a task is added, the plan rebuilds itself by priority: higher-priority tasks are placed first, and a task is kept only if it doesn't overlap one already kept. Ties go to the shorter task, then the earlier one. A higher-priority task bumps lower ones, which `addTasks()` returns. A losing task raises `ValueError`, and duplicates (same pet, type, and start) are rejected. `tryAddTask()` wraps `addTasks()` and returns warning strings instead of raising. The greedy pass does not always maximize total priority. |
| Recurring tasks | `Task.setRecurrence(recurrence)`, `Task.setDueDate(date)`, `Task.markTaskComplete()`; `PlanSchedule.markPlanComplete()` | A task is `"daily"` or `"weekly"` (or `None` for a one-off). Completing it returns a new pending copy due 1 or 7 days later, and completing an already-complete task returns `None`. `markPlanComplete()` returns the next occurrences for the caller to add to the later day's plan. |

## Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. Add a pet owner with their information, which is name, email, and phone as their contact information. 

2. Add a pet with its information. First, select which pet owner the pet belongs to, then it's name, species, breed(optional), age, and gender, along with pet category of the pet (e.g. mammal).

3. Select a specific pet to create a task, given the type (e.g. Walk), start time, duration, and priority. Owner note is optional; some pet owners might have special need when performing daily task.

4. Once the task is created, it will automatically check if this task can fit into the current schedule; if yes, it will automatically be added to the schedule; if no, it will be moved to unscheduled tasks with a given reason why it doesn't fit. If in the current schedule, there is a slot where the current high-priority task can fit by replacing a task with lower priority, the program will do so. 

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
