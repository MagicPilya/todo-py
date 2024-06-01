import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import json
import os
from datetime import datetime

MAX_TASK_TITLE_LENGTH = 50

class Task:
    def __init__(self, title, deadline):
        self.title = title
        self.deadline = deadline

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Todo List")

        self.tasks = self.load_tasks()
        self.archive = self.load_archive()

        self.task_frame = tk.Frame(root)
        self.task_frame.pack(pady=10)

        self.entry_frame = tk.Frame(root)
        self.entry_frame.pack(pady=10)

        self.entry = tk.Entry(
            self.entry_frame,
            font=("Helvetica", 12),
            width=MAX_TASK_TITLE_LENGTH
        )
        self.entry.pack(side=tk.LEFT, padx=10)

        self.deadline_entry = DateEntry(
            self.entry_frame,
            font=("Helvetica", 12),
            date_pattern="yyyy-MM-dd"
        )
        self.deadline_entry.pack(side=tk.LEFT, padx=10)

        self.add_button = tk.Button(
            self.entry_frame,
            text="Add Task",
            command=self.add_task,
            font=("Helvetica", 12)
        )
        self.add_button.pack(side=tk.LEFT, padx=10)

        self.archive_button = tk.Button(
            self.entry_frame,
            text="View Archive",
            command=self.view_archive,
            font=("Helvetica", 12)
        )
        self.archive_button.pack(side=tk.LEFT, padx=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.update_task_frame()

        # Привязка события нажатия клавиши Enter к методу add_task
        self.entry.bind("<Return>", lambda event: self.add_task())

    def load_tasks(self):
        if os.path.exists("tasks.json"):
            with open("tasks.json", "r") as file:
                tasks_data = json.load(file)
                return [Task(task['title'], task['deadline']) for task in tasks_data]
        return []

    def save_tasks(self):
        with open("tasks.json", "w") as file:
            json.dump([{'title': task.title, 'deadline': task.deadline} for task in self.tasks], file)

    def load_archive(self):
        if os.path.exists("archive.json"):
            with open("archive.json", "r") as file:
                archive_data = json.load(file)
                for task in archive_data:
                    if 'completed' not in task:
                        task['completed'] = 'N/A'  # Default value if 'completed' key is missing
                return archive_data
        return []

    def save_archive(self):
        with open("archive.json", "w") as file:
            json.dump(self.archive, file)

    def add_task(self):
        title = self.entry.get()
        deadline = self.deadline_entry.get_date().strftime('%Y-%m-%d')
        if title and deadline:
            if len(title) > MAX_TASK_TITLE_LENGTH:
                messagebox.showwarning("Warning", f"Task title must be less than {MAX_TASK_TITLE_LENGTH} characters.")
                return
            new_task = Task(title, deadline)
            self.tasks.append(new_task)
            self.update_task_frame()
            self.entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "You must enter a task and deadline.")

    def delete_task(self, task_index):
        del self.tasks[task_index]
        self.update_task_frame()

    def edit_task(self, task_index):
        task = self.tasks[task_index]

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Task")

        def edit_cancel(event=None):
            edit_window.destroy()

        # Привязываем событие нажатия Esc к методу edit_cancel
        edit_window.bind("<Escape>", edit_cancel)

        title_label = tk.Label(edit_window, text="Task Title:", font=("Helvetica", 12))
        title_label.pack(pady=5)

        title_entry = tk.Entry(edit_window, font=("Helvetica", 12), width=MAX_TASK_TITLE_LENGTH)
        title_entry.pack(pady=5)
        title_entry.insert(0, task.title)

        # Привязываем событие нажатия Enter к методу save_changes
        title_entry.bind("<Return>", lambda event: save_changes())

        deadline_label = tk.Label(edit_window, text="Deadline:", font=("Helvetica", 12))
        deadline_label.pack(pady=5)

        deadline_entry = DateEntry(edit_window, font=("Helvetica", 12), date_pattern="yyyy-MM-dd")
        deadline_entry.pack(pady=5)
        deadline_entry.set_date(datetime.strptime(task.deadline, '%Y-%m-%d'))

        # Привязываем событие нажатия Enter к методу save_changes
        deadline_entry.bind("<Return>", lambda event: save_changes())

        def save_changes():
            new_title = title_entry.get()
            new_deadline = deadline_entry.get_date().strftime('%Y-%m-%d')
            if new_title and new_deadline:
                if len(new_title) > MAX_TASK_TITLE_LENGTH:
                    messagebox.showwarning("Warning", f"Task title must be less than {MAX_TASK_TITLE_LENGTH} characters.")
                    return
                self.tasks[task_index] = Task(new_title, new_deadline)
                self.update_task_frame()
                edit_window.destroy()
            else:
                messagebox.showwarning("Warning", "You must enter a task and deadline.")

        save_button = tk.Button(edit_window, text="Save", command=save_changes, font=("Helvetica", 12))
        save_button.pack(pady=5)


    def mark_task_done(self, task_index):
        completed_task = self.tasks[task_index]
        self.archive.append({'title': completed_task.title, 'completed': datetime.now().strftime('%Y-%m-%d'), 'deadline': completed_task.deadline})
        del self.tasks[task_index]
        self.save_archive()
        self.update_task_frame()

    def update_task_frame(self):
        for widget in self.task_frame.winfo_children():
            widget.destroy()
        if not self.tasks:
            no_task_label = tk.Label(
                self.task_frame,
                text="No tasks available.",
                font=("Helvetica", 12),
                fg="grey"
            )
            no_task_label.pack(pady=10)
        else:
            for index, task in enumerate(self.tasks):
                task_frame = tk.Frame(self.task_frame, bd=1, relief="solid")
                task_frame.pack(fill="x", pady=2)

                task_label = tk.Label(task_frame, text=f"{task.title} (Deadline: {task.deadline})", font=("Helvetica", 12))
                task_label.pack(side=tk.LEFT, padx=10)

                edit_button = tk.Button(task_frame, text="Edit", command=lambda idx=index: self.edit_task(idx), font=("Helvetica", 12))
                edit_button.pack(side=tk.LEFT, padx=5)

                done_button = tk.Button(task_frame, text="Done", command=lambda idx=index: self.mark_task_done(idx), font=("Helvetica", 12))
                done_button.pack(side=tk.LEFT, padx=5)

                delete_button = tk.Button(task_frame, text="Delete", command=lambda idx=index: self.delete_task(idx), font=("Helvetica", 12))
                delete_button.pack(side=tk.LEFT, padx=5)

    def view_archive(self):
        archive_window = tk.Toplevel(self.root)
        archive_window.title("Archive")

        columns = ["Task Title", "Completed Date", "Deadline", "Restore", "Delete"]
        max_title_length = MAX_TASK_TITLE_LENGTH

        for col_num, col_name in enumerate(columns):
            header = tk.Label(archive_window, text=col_name, font=("Helvetica", 12, "bold"))
            header.grid(row=0, column=col_num, padx=5, pady=5, sticky="w")

        for row_num, task in enumerate(self.archive, start=1):
            title_label = tk.Label(archive_window, text=task['title'], font=("Helvetica", 12), width=max_title_length)
            title_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="w")

            completed_label = tk.Label(archive_window, text=task.get('completed', 'N/A'), font=("Helvetica", 12))
            completed_label.grid(row=row_num, column=1, padx=5, pady=5, sticky="w")

            deadline_label = tk.Label(archive_window, text=task['deadline'], font=("Helvetica", 12))
            deadline_label.grid(row=row_num, column=2, padx=5, pady=5, sticky="w")

            restore_button = tk.Button(archive_window, text="Restore", command=lambda idx=row_num-1: self.restore_task(idx), font=("Helvetica", 12))
            restore_button.grid(row=row_num, column=3, padx=5, pady=5)

            delete_button = tk.Button(archive_window, text="Delete", command=lambda idx=row_num-1: self.delete_from_archive(idx, archive_window), font=("Helvetica", 12))
            delete_button.grid(row=row_num, column=4, padx=5, pady=5)

    def restore_task(self, task_index):
        task = self.archive[task_index]
        self.tasks.append(Task(task['title'], task['deadline']))
        del self.archive[task_index]
        self.save_archive()
        self.update_task_frame()

    def delete_from_archive(self, task_index, archive_window):
        del self.archive[task_index]
        self.save_archive()
        archive_window.destroy()
        self.view_archive()

    def on_closing(self):
        self.save_tasks()
        self.save_archive()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
