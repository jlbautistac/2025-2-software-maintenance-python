import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

TASKS_FILE = "tasks.json"

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        self.root.geometry("700x500")

        self.users = {
            "admin": {"password": "admin123", "role": "admin"},
            "user": {"password": "user123", "role": "user"}
        }

        self.tasks = self.load_tasks()
        self.selected_task_id = None
        self.username = None
        self.role = None

        self.login_screen()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def login_screen(self):
        self.clear_window()
        frame = tk.Frame(self.root)
        frame.pack(pady=100)

        tk.Label(frame, text="Username:").grid(row=0, column=0, sticky="e")
        tk.Label(frame, text="Password:").grid(row=1, column=0, sticky="e")

        self.username_entry = tk.Entry(frame)
        self.password_entry = tk.Entry(frame, show="*")
        self.username_entry.grid(row=0, column=1, pady=5)
        self.password_entry.grid(row=1, column=1, pady=5)

        tk.Button(frame, text="Login", command=self.login).grid(row=2, column=0, columnspan=2, pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        user = self.users.get(username)
        if user and user["password"] == password:
            self.username = username
            self.role = user["role"]
            self.main_screen()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def main_screen(self):
        self.clear_window()

        logout_button = tk.Button(self.root, text="Logout", command=self.logout)
        logout_button.pack(anchor="ne", padx=10, pady=5)

        if self.role == "admin":
            form_frame = tk.Frame(self.root)
            form_frame.pack(pady=10)

            tk.Label(form_frame, text="Title:").grid(row=0, column=0)
            self.title_entry = tk.Entry(form_frame)
            self.title_entry.grid(row=0, column=1)

            tk.Label(form_frame, text="Description:").grid(row=1, column=0)
            self.desc_entry = tk.Entry(form_frame)
            self.desc_entry.grid(row=1, column=1)

            tk.Label(form_frame, text="Due Date (YYYY-MM-DD):").grid(row=2, column=0)
            self.date_entry = tk.Entry(form_frame)
            self.date_entry.grid(row=2, column=1)

            button_frame = tk.Frame(self.root)
            button_frame.pack(pady=5)

            tk.Button(button_frame, text="Add Task", command=self.add_task).pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="Edit Task", command=self.edit_task).pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="Delete Task", command=self.delete_task).pack(side=tk.LEFT, padx=5)

        complete_button = tk.Button(self.root, text="Mark as Completed", command=self.complete_task)
        complete_button.pack(pady=5)

        self.tree = ttk.Treeview(self.root, columns=("Title", "Description", "Due Date", "Completed"), show="headings")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Due Date", text="Due Date")
        self.tree.heading("Completed", text="Completed")
        self.tree.bind("<<TreeviewSelect>>", self.on_task_select)
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        self.load_treeview()

    def logout(self):
        self.save_tasks()
        self.username = None
        self.role = None
        self.selected_task_id = None
        self.tasks = self.load_tasks()  # recarga por si cambió
        self.clear_window()
        self.login_screen()

    def load_treeview(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for task in self.tasks:
            self.tree.insert("", tk.END, iid=task["id"], values=(
                task["title"],
                task["description"],
                task["due_date"],
                "Yes" if task["completed"] else "No"
            ))

    def add_task(self):
        title = self.title_entry.get().strip()
        desc = self.desc_entry.get().strip()
        due_date = self.date_entry.get().strip()

        if not title or not due_date:
            messagebox.showwarning("Warning", "Title and Due Date are required")
            return

        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Due Date must be in YYYY-MM-DD format")
            return

        new_id = max([task["id"] for task in self.tasks], default=0) + 1
        self.tasks.append({
            "id": new_id,
            "title": title,
            "description": desc,
            "due_date": due_date,
            "completed": False
        })
        self.save_tasks()
        self.load_treeview()
        self.clear_form()

    def edit_task(self):
        if self.selected_task_id is None:
            messagebox.showwarning("Warning", "Select a task to edit")
            return

        title = self.title_entry.get().strip()
        desc = self.desc_entry.get().strip()
        due_date = self.date_entry.get().strip()

        if not title or not due_date:
            messagebox.showwarning("Warning", "Title and Due Date are required")
            return

        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Due Date must be in YYYY-MM-DD format")
            return

        for task in self.tasks:
            if task["id"] == self.selected_task_id:
                task["title"] = title
                task["description"] = desc
                task["due_date"] = due_date
                break

        self.save_tasks()
        self.load_treeview()
        self.clear_form()

    def delete_task(self):
        if self.selected_task_id is None:
            messagebox.showwarning("Warning", "Select a task to delete")
            return

        self.tasks = [t for t in self.tasks if t["id"] != self.selected_task_id]
        self.save_tasks()
        self.load_treeview()
        self.clear_form()

    def complete_task(self):
        if self.selected_task_id is None:
            messagebox.showwarning("Warning", "Select a task to mark completed")
            return

        for task in self.tasks:
            if task["id"] == self.selected_task_id:
                task["completed"] = True
                break

        self.save_tasks()
        self.load_treeview()
        self.clear_form()

    def on_task_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.selected_task_id = int(selected[0])
            task = next((t for t in self.tasks if t["id"] == self.selected_task_id), None)
            if task and self.role == "admin":
                self.title_entry.delete(0, tk.END)
                self.title_entry.insert(0, task["title"])

                self.desc_entry.delete(0, tk.END)
                self.desc_entry.insert(0, task["description"])

                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, task["due_date"])
        else:
            self.selected_task_id = None

    def clear_form(self):
        if self.role == "admin":
            self.title_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
            self.date_entry.delete(0, tk.END)
        self.selected_task_id = None

    def save_tasks(self):
        with open(TASKS_FILE, "w") as f:
            json.dump(self.tasks, f, indent=4)

    def load_tasks(self):
        if not os.path.exists(TASKS_FILE):
            return []
        with open(TASKS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()
