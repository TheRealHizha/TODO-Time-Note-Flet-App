import flet as ft
from datetime import datetime
import json
import os
import time
import threading

# File to store app data
DATA_FILE = "app_data.json"

# Todo functions
todo_items = []
new_task_field = None
todo_list_view = None

def add_todo(e):
    """Add a new todo item to the list"""
    if new_task_field.value:
        create_todo_item(new_task_field.value)
        new_task_field.value = ""
        save_data()
        e.page.update()

def create_todo_item(task_name, completed=False):
    """Create a new todo item with edit/delete functionality"""
    checkbox = ft.Checkbox(value=completed)
    task_text = ft.Text(task_name, size=16)
    
    def delete_clicked(e):
        """Remove todo item from list and update storage"""
        todo_list_view.controls.remove(row)
        todo_items[:] = [item for item in todo_items if item["row"] != row]
        save_data()
        e.page.update()
    
    def edit_clicked(e):
        """Switch to edit mode for todo item"""
        edit_field.value = task_text.value
        display_row.visible = False
        edit_row.visible = True
        e.page.update()
    
    def save_clicked(e):
        """Save edited todo item and switch back to display mode"""
        task_text.value = edit_field.value
        display_row.visible = True
        edit_row.visible = False
        save_data()
        e.page.update()
    
    # Create edit field and controls
    edit_field = ft.TextField(value=task_name, expand=True)
    
    # Display view (normal mode)
    display_row = ft.Row(
        alignment="spaceBetween",
        controls=[
            checkbox,
            task_text,
            ft.Row(
                controls=[
                    ft.IconButton(
                        icon="edit",
                        tooltip="Edit",
                        on_click=edit_clicked,
                    ),
                    ft.IconButton(
                        icon="delete",
                        tooltip="Delete",
                        on_click=delete_clicked,
                    ),
                ],
            ),
        ],
    )
    
    # Edit view (edit mode)
    edit_row = ft.Row(
        visible=False,
        alignment="spaceBetween",
        controls=[
            edit_field,
            ft.IconButton(
                icon="done",
                icon_color="green",
                tooltip="Update",
                on_click=save_clicked,
            ),
        ],
    )
    
    # Create the todo item container
    row = ft.Column(controls=[display_row, edit_row])
    todo_list_view.controls.append(row)
    todo_items.append({
        "row": row,
        "checkbox": checkbox,
        "task_text": task_text,
        "name": task_name,
        "completed": completed
    })

# Time Tracker
start_time = None
elapsed_time = 0
timer_running = False
time_display = None
start_button = None
stop_button = None
reset_button = None
timer_thread = None

def start_timer(e):
    """Start the timer and background thread"""
    global start_time, timer_running, timer_thread
    if not timer_running:
        start_time = datetime.now()
        timer_running = True
        start_button.disabled = True
        stop_button.disabled = False
        e.page.update()
        
        # Start timer thread for background operation
        timer_thread = threading.Thread(target=update_timer, args=(e.page,), daemon=True)
        timer_thread.start()

def stop_timer(e):
    """Stop the timer and calculate elapsed time"""
    global timer_running, elapsed_time
    if timer_running:
        timer_running = False
        start_button.disabled = False
        stop_button.disabled = True
        elapsed_time += int((datetime.now() - start_time).total_seconds()) if start_time else 0
        e.page.update()

def reset_timer(e):
    """Reset the timer to zero"""
    global timer_running, elapsed_time, start_time
    timer_running = False
    elapsed_time = 0
    start_time = None
    time_display.value = "00:00:00"
    start_button.disabled = False
    stop_button.disabled = True
    e.page.update()

def update_timer(page):
    """Background timer update function running in separate thread"""
    global timer_thread
    while timer_running:
        if start_time:
            # Calculate total elapsed time
            elapsed = datetime.now() - start_time
            total_seconds = int(elapsed.total_seconds()) + elapsed_time
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_display.value = f"{hours:02}:{minutes:02}:{seconds:02}"
            page.update()
        time.sleep(1)  # Update every second

# Notes functions
notes_items = []
notes_list_view = None

def add_note(e):
    """Add a new empty note"""
    create_note_item("New Note", "")
    save_data()
    e.page.update()

def create_note_item(title, content):
    """Create a new note with delete functionality"""
    def delete_clicked(e):
        """Remove note from list and update storage"""
        notes_list_view.controls.remove(note_container)
        notes_items[:] = [item for item in notes_items if item["container"] != note_container]
        save_data()
        e.page.update()
    
    # Create note fields
    title_field = ft.TextField(
        value=title,
        label="Title",
        text_size=20,
        border="none",
        filled=False
    )
    
    content_field = ft.TextField(
        value=content,
        multiline=True,
        min_lines=3,
        max_lines=10,
        border="outline"
    )
    
    # Create note container with styling
    note_container = ft.Container(
        content=ft.Column(
            controls=[
                title_field,
                content_field,
                ft.Row(
                    alignment="end",
                    controls=[
                        ft.IconButton(
                            icon="delete",
                            tooltip="Delete Note",
                            on_click=delete_clicked
                        )
                    ]
                )
            ]
        ),
        border=ft.border.all(1, "outline"),
        border_radius=5,
        padding=10,
        margin=ft.margin.only(bottom=10)
    )
    
    # Add to view and tracking list
    notes_list_view.controls.append(note_container)
    notes_items.append({
        "container": note_container,
        "title_field": title_field,
        "content_field": content_field
    })

# Data functions
def load_data():
    """
    Load saved data from JSON file with error handling
    Returns a dictionary with 'todos' and 'notes' lists
    """
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                # Ensure data has the correct structure
                if isinstance(data, dict):
                    todos = data.get("todos", [])
                    notes = data.get("notes", [])
                    # Validate structure
                    if not isinstance(todos, list):
                        todos = []
                    if not isinstance(notes, list):
                        notes = []
                    return {
                        "todos": todos,
                        "notes": notes
                    }
                else:
                    # If data is not a dict, return empty structure
                    return {"todos": [], "notes": []}
        except (json.JSONDecodeError, Exception):
            # If file is corrupted or has wrong structure, return empty structure
            return {"todos": [], "notes": []}
    return {"todos": [], "notes": []}

def save_data():
    """
    Save current app data to JSON file with validation
    Prevents data corruption by validating structure before saving
    """
    # Validate and prepare todo items
    todos_data = []
    for item in todo_items:
        try:
            todos_data.append({
                "task": item["task_text"].value,
                "completed": item["checkbox"].value
            })
        except Exception:
            pass  # Skip invalid items
    
    # Validate and prepare note items
    notes_data = []
    for item in notes_items:
        try:
            notes_data.append({
                "title": item["title_field"].value,
                "content": item["content_field"].value
            })
        except Exception:
            pass  # Skip invalid items
    
    # Create data structure
    data = {
        "todos": todos_data,
        "notes": notes_data
    }
    
    # Save to file with error handling
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving  {e}")

def main(page: ft.Page):
    """
    Main application entry point
    Sets up the UI with tabs for Todos, Time, and Notes
    """
    global new_task_field, todo_list_view, time_display, start_button, stop_button, reset_button, notes_list_view
    
    # Page configuration
    page.title = "Todo, Time & Notes App"
    page.horizontal_alignment = "center"
    page.scroll = "adaptive"
    
    # Load saved data
    data = load_data()
    
    # Todo Tab
    new_task_field = ft.TextField(
        hint_text="What needs to be done?",
        expand=True,
        on_submit=add_todo
    )
    
    todo_list_view = ft.Column(spacing=10)
    
    # Load saved todos with validation
    todos = data.get("todos", [])
    if isinstance(todos, list):
        for todo in todos:
            if isinstance(todo, dict):
                task = todo.get("task", "")
                completed = todo.get("completed", False)
                if isinstance(task, str) and isinstance(completed, bool):
                    create_todo_item(task, completed)
    
    todo_tab = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    new_task_field,
                    ft.FloatingActionButton(
                        icon="add",
                        on_click=add_todo
                    )
                ]
            ),
            ft.Divider(),
            todo_list_view
        ]
    )
    
    # Time Tab
    time_display = ft.Text(
        value="00:00:00",
        size=32,
        weight="bold",
        text_align="center"
    )
    
    start_button = ft.ElevatedButton(
        text="Start",
        on_click=start_timer
    )
    
    stop_button = ft.ElevatedButton(
        text="Stop",
        on_click=stop_timer,
        disabled=True
    )
    
    reset_button = ft.ElevatedButton(
        text="Reset",
        on_click=reset_timer
    )
    
    time_tab = ft.Column(
        horizontal_alignment="center",
        controls=[
            ft.Text("Time Tracker", size=24, weight="bold"),
            time_display,
            ft.Row(
                controls=[
                    start_button,
                    stop_button,
                    reset_button
                ]
            )
        ]
    )
    
    # Notes Tab
    notes_list_view = ft.Column(spacing=20)
    
    # Load saved notes with validation
    notes = data.get("notes", [])
    if isinstance(notes, list):
        for note in notes:
            if isinstance(note, dict):
                title = note.get("title", "New Note")
                content = note.get("content", "")
                if isinstance(title, str) and isinstance(content, str):
                    create_note_item(title, content)
            else:
                # Handle case where note is not a dict (backward compatibility)
                create_note_item("New Note", "")
    
    notes_tab = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text("Notes", size=24, weight="bold"),
                    ft.IconButton(
                        icon="add",
                        tooltip="Add Note",
                        on_click=add_note
                    )
                ],
                alignment="spaceBetween"
            ),
            ft.Divider(),
            notes_list_view
        ]
    )
    
    # Create tabs interface
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Todo",
                icon="check_box",
                content=todo_tab
            ),
            ft.Tab(
                text="Time",
                icon="timer",
                content=time_tab
            ),
            ft.Tab(
                text="Notes",
                icon="notes",
                content=notes_tab
            ),
        ],
        expand=1
    )
    
    page.add(tabs)

# Run the application
ft.app(target=main)
