from datetime import date, time

import streamlit as st

from pawpal_system import Owner, Pet, Priority, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' daily care tasks and get an explained schedule.")

# st.session_state is a dict-like "vault" that survives Streamlit reruns (every click reruns this
# script top to bottom). Only create the Owner if the vault doesn't already hold one.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=120)
owner: Owner = st.session_state.owner

# ---------------------------------------------------------------- Owner
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.available_minutes = int(
        st.number_input("Minutes available today", min_value=1, max_value=1440, value=owner.available_minutes)
    )

st.divider()

# ---------------------------------------------------------------- Add a pet
st.subheader("Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        pet_name = st.text_input("Pet name")
        breed = st.text_input("Breed")
    with c2:
        weight = st.number_input("Weight (lbs)", min_value=0.0, value=10.0, step=0.5)
        age = st.number_input("Age (years)", min_value=0, max_value=40, value=1)
    if st.form_submit_button("Add pet"):
        if pet_name.strip():
            owner.add_pet(Pet(name=pet_name.strip(), breed=breed.strip(), weight=float(weight), age=int(age)))
            st.success(f"Added {pet_name.strip()}!")
        else:
            st.error("Please enter a pet name.")

if owner.pets:
    st.table(
        [{"Name": p.name, "Breed": p.breed, "Weight": p.weight, "Age": p.age, "Tasks": len(p.tasks)} for p in owner.pets]
    )
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ---------------------------------------------------------------- Schedule a task
st.subheader("Schedule a Task")
if not owner.pets:
    st.info("Add a pet before scheduling tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        pet_index = st.selectbox("For which pet?", range(len(owner.pets)), format_func=lambda i: owner.pets[i].name)
        c1, c2, c3 = st.columns(3)
        with c1:
            task_title = st.text_input("Task title", value="Morning walk")
            category = st.text_input("Category", value="exercise")
        with c2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            priority_name = st.selectbox("Priority", [p.name.capitalize() for p in Priority], index=2)
        with c3:
            frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])
            use_time = st.checkbox("Set a preferred time")
            preferred = st.time_input("Preferred time", value=time(8, 0))
        if st.form_submit_button("Add task"):
            task = Task(
                title=task_title.strip() or "Untitled task",
                category=category.strip(),
                duration_minutes=int(duration),
                priority=Priority[priority_name.upper()],
                frequency=frequency,
                preferred_time=preferred if use_time else None,
            )
            owner.pets[pet_index].add_task(task)
            st.success(f"Added '{task.title}' to {owner.pets[pet_index].name}.")

    # Filter and sort the task list using the Scheduler's methods.
    scheduler = Scheduler(owner)
    f1, f2 = st.columns(2)
    with f1:
        pet_filter = st.selectbox("Show pet", ["All"] + [p.name for p in owner.pets])
    with f2:
        status_filter = st.selectbox("Show status", ["All", "To do", "Done"])
    completed_filter = {"All": None, "To do": False, "Done": True}[status_filter]
    shown = scheduler.sort_by_time(
        scheduler.filter_tasks(pet_name=None if pet_filter == "All" else pet_filter, completed=completed_filter)
    )
    pet_name_of = {id(t): pet.name for pet in owner.pets for t in pet.tasks}
    if shown:
        st.table(
            [
                {
                    "Pet": pet_name_of[id(t)],
                    "Task": t.title,
                    "Minutes": t.duration_minutes,
                    "Priority": t.priority.name.capitalize(),
                    "Repeats": t.frequency,
                    "Due": t.due_date.isoformat(),
                    "Preferred time": f"{t.preferred_time:%H:%M}" if t.preferred_time else "-",
                    "Done": t.completed,
                }
                for t in shown
            ]
        )
    else:
        st.info("No matching tasks.")

    pending = [(pet, t) for pet in owner.pets for t in pet.tasks if not t.completed]
    if pending:
        with st.form("complete_task_form"):
            pick = st.selectbox(
                "Mark a task complete",
                range(len(pending)),
                format_func=lambda i: f"{pending[i][0].name}: {pending[i][1].title} (due {pending[i][1].due_date})",
            )
            if st.form_submit_button("Complete"):
                pet, task = pending[pick]
                next_task = scheduler.mark_task_complete(pet, task)
                st.success(
                    f"Completed '{task.title}'."
                    + (f" Next one is due {next_task.due_date}." if next_task else "")
                )
                st.rerun()

    for warning in scheduler.find_time_conflicts(date.today()):
        st.warning(f"Time conflict: {warning}")

st.divider()

# ---------------------------------------------------------------- Build schedule
st.subheader("Today's Schedule")
if st.button("Generate schedule"):
    if not owner.get_all_tasks():
        st.warning("Add at least one task first.")
    else:
        plan = Scheduler(owner).generate_plan(date.today())
        st.success(f"{len(plan.items)} task(s) scheduled, {plan.total_minutes} of {owner.available_minutes} min used.")
        st.table(
            [
                {
                    "Time": f"{i.start_time:%H:%M}-{i.end_time:%H:%M}",
                    "Pet": i.pet.name,
                    "Task": i.task.title,
                    "Why": i.reason,
                }
                for i in plan.items
            ]
        )
        if plan.skipped_tasks:
            st.warning(
                "Skipped (not enough time): " + ", ".join(f"{t.title} ({t.duration_minutes} min)" for t in plan.skipped_tasks)
            )
