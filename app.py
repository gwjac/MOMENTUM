import streamlit as st
from datetime import datetime
import json
import os

# App title
st.set_page_config(page_title="Momentum", page_icon="🚀", layout="wide")
st.title("🚀 Momentum")

# File for persistence (local testing; cloud uses session state)
DATA_FILE = "momentum_data.json"

# Load data from file (local) or session state (cloud)
def load_data():
    if 'todo_tasks' not in st.session_state:
        st.session_state.todo_tasks = []
        st.session_state.doing_tasks = []
        st.session_state.done_tasks = []
    if os.getenv('STREAMLIT_CLOUD'):  # Cloud mode
        return
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            st.session_state.todo_tasks = data.get('todo', [])
            st.session_state.doing_tasks = data.get('doing', [])
            st.session_state.done_tasks = data.get('done', [])
            st.info(f"Loaded {len(st.session_state.todo_tasks) + len(st.session_state.doing_tasks) + len(st.session_state.done_tasks)} tasks!")
    else:
        st.info("New session—add your first task!")

load_data()

# Helper to generate timestamp
def get_timestamp():
    now = datetime.now()
    return now.strftime("%H:%M %d %b %Y").upper()

# Helper to move task
def move_task(tasks_list, task_index, new_list):
    if 0 <= task_index < len(tasks_list):
        task = tasks_list.pop(task_index)
        if new_list == st.session_state.done_tasks:
            task = f"{task} - {get_timestamp()}"
        new_list.append(task)
    save_data()
    st.rerun()

# Delete task
def delete_task(list_name, index):
    if list_name == 'todo':
        del st.session_state.todo_tasks[index]
    elif list_name == 'doing':
        del st.session_state.doing_tasks[index]
    elif list_name == 'done':
        del st.session_state.done_tasks[index]
    save_data()
    st.rerun()

# Add task
def add_task():
    new_todo = st.session_state.get('new_todo', '')
    if new_todo:
        st.session_state.todo_tasks.append(new_todo)
        st.session_state.new_todo = ''
    save_data()
    st.rerun()

# Save data to file (local) or session state (cloud)
def save_data():
    data = {
        'todo': st.session_state.todo_tasks,
        'doing': st.session_state.doing_tasks,
        'done': st.session_state.done_tasks
    }
    if not os.getenv('STREAMLIT_CLOUD'):  # Local mode
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)

# Tabs
tab1, tab2, tab3 = st.tabs(["📝 To Do", "⚡ Doing", "✅ Done"])

with tab1:
    st.header("To Do List")
    st.text_input("Add a new task:", key="new_todo")
    st.button("Add Task", on_click=add_task)
    
    if st.session_state.todo_tasks:
        for i, task in enumerate(st.session_state.todo_tasks):
            col1, col2, col3, col4, col5 = st.columns([3, 0.5, 0.5, 1, 0.5])
            with col1:
                st.write(f"{i+1}. {task}")
            with col2:
                if st.button("↑", key=f"up_todo_{i}"):
                    if i > 0:
                        st.session_state.todo_tasks[i], st.session_state.todo_tasks[i-1] = st.session_state.todo_tasks[i-1], st.session_state.todo_tasks[i]
                        save_data()
                        st.rerun()
            with col3:
                if st.button("↓", key=f"down_todo_{i}"):
                    if i < len(st.session_state.todo_tasks) - 1:
                        st.session_state.todo_tasks[i], st.session_state.todo_tasks[i+1] = st.session_state.todo_tasks[i+1], st.session_state.todo_tasks[i]
                        save_data()
                        st.rerun()
            with col4:
                if st.button("Move to Doing", key=f"move_todo_{i}"):
                    move_task(st.session_state.todo_tasks, i, st.session_state.doing_tasks)
            with col5:
                if st.button("🗑️", key=f"del_todo_{i}"):
                    delete_task('todo', i)
    else:
        st.info("No tasks yet. Add one above!")

with tab2:
    st.header("Doing List")
    if st.session_state.doing_tasks:
        for i, task in enumerate(st.session_state.doing_tasks):
            col1, col2, col3, col4, col5, col6 = st.columns([3, 0.5, 0.5, 1, 1, 0.5])
            with col1:
                st.write(f"{i+1}. {task}")
            with col2:
                if st.button("↑", key=f"up_doing_{i}"):
                    if i > 0:
                        st.session_state.doing_tasks[i], st.session_state.doing_tasks[i-1] = st.session_state.doing_tasks[i-1], st.session_state.doing_tasks[i]
                        save_data()
                        st.rerun()
            with col3:
                if st.button("↓", key=f"down_doing_{i}"):
                    if i < len(st.session_state.doing_tasks) - 1:
                        st.session_state.doing_tasks[i], st.session_state.doing_tasks[i+1] = st.session_state.doing_tasks[i+1], st.session_state.doing_tasks[i]
                        save_data()
                        st.rerun()
            with col4:
                if st.button("Back to To Do", key=f"back_doing_{i}"):
                    move_task(st.session_state.doing_tasks, i, st.session_state.todo_tasks)
            with col5:
                if st.button("Mark Done", key=f"done_doing_{i}"):
                    move_task(st.session_state.doing_tasks, i, st.session_state.done_tasks)
            with col6:
                if st.button("🗑️", key=f"del_doing_{i}"):
                    delete_task('doing', i)
    else:
        st.info("No tasks in progress. Move some from To Do!")

with tab3:
    st.header("Done List")
    if st.session_state.done_tasks:
        for i, task in enumerate(st.session_state.done_tasks):
            col1, col2 = st.columns([3, 0.5])
            with col1:
                st.write(f"{i+1}. {task}")
            with col2:
                if st.button("🗑️", key=f"del_done_{i}"):
                    delete_task('done', i)
    else:
        st.info("Nothing done yet. Keep going!")

# Save on every run (including refresh)
save_data()