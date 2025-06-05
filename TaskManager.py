import os
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime


class TaskManager:
    # Clase encargada de manejar las tareas: cargar, guardar, agregar, eliminar, editar, etc.
    def __init__(self, filename="tasks.json"):
        self.filename = filename  # Archivo donde se guardan las tareas
        self.tasks = []           # Lista que almacena las tareas en memoria
        self.load_tasks()         # Al iniciar carga las tareas desde el archivo

    def load_tasks(self):
        # Carga las tareas desde el archivo JSON si existe
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    self.tasks = json.load(f)
            except:
                self.tasks = []  # Si hay error, inicializa lista vacía

    def save_tasks(self):
        # Guarda la lista de tareas en el archivo JSON
        with open(self.filename, "w") as f:
            json.dump(self.tasks, f, indent=2)

    def get_next_id(self):
        # Devuelve el siguiente ID para una nueva tarea, basado en el máximo actual + 1
        if not self.tasks:
            return 1
        return max(task["id"] for task in self.tasks) + 1

    def add_task(self, title, description):
        # Añade una tarea nueva con título, descripción, estado pendiente y fecha actual
        task = {
            "id": self.get_next_id(),
            "title": title,
            "description": description,
            "status": "Pending",
            "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.tasks.append(task)
        self.save_tasks()

    def delete_task(self, task_id):
        # Elimina la tarea cuyo ID coincide con task_id
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        self.save_tasks()

    def mark_complete(self, task_id):
        # Marca una tarea como completada buscando por ID
        for task in self.tasks:
            if task["id"] == task_id:
                task["status"] = "Completed"
                break
        self.save_tasks()

    def edit_task(self, task_id, new_title, new_description):
        # Edita el título y descripción de una tarea por su ID
        for task in self.tasks:
            if task["id"] == task_id:
                task["title"] = new_title
                task["description"] = new_description
                break
        self.save_tasks()

    def search_tasks(self, keyword="", status_filter=None):
        # Busca tareas filtrando por palabra clave y estado (Pending, Completed o None para todos)
        keyword = keyword.lower()
        result = []
        for task in self.tasks:
            # Busca si la palabra clave está en título o descripción
            if keyword in task["title"].lower() or keyword in task["description"].lower():
                # Filtra por estado si se especifica
                if status_filter is None or task["status"] == status_filter:
                    result.append(task)
        return result


class TaskManagerGUI:
    # Interfaz gráfica de usuario (GUI) usando tkinter
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        self.root.geometry("700x500")          # Tamaño fijo de ventana
        self.root.configure(bg="#f0f4f8")      # Color de fondo claro
        self.root.resizable(False, False)      # Ventana no redimensionable

        self.task_manager = TaskManager()      # Instancia la lógica de tareas

        # Estilos para entradas y botones
        entry_style = {"font": ("Segoe UI", 12), "bd": 2, "relief": "groove"}
        self.btn_style = {
            "font": ("Segoe UI", 11, "bold"),
            "bg": "#3498db",
            "fg": "white",
            "activebackground": "#2980b9",
            "activeforeground": "white",
            "bd": 0,
            "width": 12,
            "cursor": "hand2",
        }

        # Frame para barra de búsqueda y filtro de estado
        search_frame = tk.Frame(root, bg="#f0f4f8")
        search_frame.pack(pady=10)

        # Caja de texto para buscar tareas por palabra clave
        self.search_entry = tk.Entry(search_frame, width=40, **entry_style)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_tasks())  # Actualiza lista al escribir

        # Menú desplegable para filtrar por estado: All, Pending, Completed
        self.status_var = tk.StringVar()
        self.status_var.set("All")
        status_menu = tk.OptionMenu(search_frame, self.status_var, "All", "Pending", "Completed", command=lambda _: self.load_tasks())
        status_menu.config(font=("Segoe UI", 11), bg="white", bd=1, relief="solid", width=10, cursor="hand2")
        status_menu["menu"].config(font=("Segoe UI", 11))
        status_menu.pack(side=tk.LEFT)

        # Frame para la lista de tareas con scrollbar
        listbox_frame = tk.Frame(root, bg="#f0f4f8")
        listbox_frame.pack(pady=10)

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Listbox para mostrar tareas
        self.task_listbox = tk.Listbox(listbox_frame, width=70, height=12, font=("Segoe UI", 11), yscrollcommand=scrollbar.set,
                                       selectbackground="#3498db", activestyle="none")
        self.task_listbox.pack()
        self.task_listbox.bind("<<ListboxSelect>>", self.show_description)  # Mostrar descripción al seleccionar

        scrollbar.config(command=self.task_listbox.yview)

        # Caja de texto para mostrar la descripción de la tarea seleccionada (solo lectura)
        self.description_text = tk.Text(root, height=5, width=60, font=("Segoe UI", 11), wrap=tk.WORD,
                                        state=tk.DISABLED, bg="white", bd=2, relief="sunken")
        self.description_text.pack(pady=10)

        # Frame para botones de acción
        button_frame = tk.Frame(root, bg="#f0f4f8")
        button_frame.pack(pady=10)

        # Botones con estilos
        self.btn_add = tk.Button(button_frame, text="Add Task", command=self.add_task, **self.btn_style)
        self.btn_add.pack(side=tk.LEFT, padx=6)

        self.btn_edit = tk.Button(button_frame, text="Edit Task", command=self.edit_task, **self.btn_style)
        self.btn_edit.pack(side=tk.LEFT, padx=6)

        self.btn_complete = tk.Button(button_frame, text="Mark Complete", command=self.mark_complete, **self.btn_style)
        self.btn_complete.pack(side=tk.LEFT, padx=6)

        self.btn_delete = tk.Button(button_frame, text="Delete Task", command=self.delete_task, **self.btn_style)
        self.btn_delete.pack(side=tk.LEFT, padx=6)

        # Botón Exit con estilo rojo diferente
        btn_exit_style = self.btn_style.copy()
        btn_exit_style["bg"] = "#e74c3c"
        btn_exit_style["activebackground"] = "#b73227"
        self.btn_exit = tk.Button(button_frame, text="Exit", command=root.quit, **btn_exit_style)
        self.btn_exit.pack(side=tk.LEFT, padx=6)

        self.load_tasks()  # Carga la lista inicial de tareas

    def load_tasks(self):
        # Limpia y carga las tareas en la listbox según búsqueda y filtro
        self.task_listbox.delete(0, tk.END)
        keyword = self.search_entry.get()
        status_filter = self.status_var.get()
        status_filter = None if status_filter == "All" else status_filter

        tasks = self.task_manager.search_tasks(keyword, status_filter)
        for task in tasks:
            display = f"[{task['id']}] {task['title']} - {task['status']}"
            self.task_listbox.insert(tk.END, display)
        self.show_description(None)  # Limpia o actualiza descripción

    def get_selected_task_id(self):
        # Obtiene el ID de la tarea seleccionada en la listbox
        selection = self.task_listbox.curselection()
        if not selection:
            return None
        task_str = self.task_listbox.get(selection[0])
        return int(task_str.split(']')[0][1:])

    def add_task(self):
        # Pide datos al usuario y agrega una tarea nueva
        title = simpledialog.askstring("Add Task", "Enter task title:")
        if title:
            desc = simpledialog.askstring("Add Task", "Enter task description:")
            self.task_manager.add_task(title, desc or "")
            self.load_tasks()

    def delete_task(self):
        # Elimina la tarea seleccionada
        task_id = self.get_selected_task_id()
        if task_id:
            self.task_manager.delete_task(task_id)
            self.load_tasks()

    def mark_complete(self):
        # Marca como completada la tarea seleccionada
        task_id = self.get_selected_task_id()
        if task_id:
            self.task_manager.mark_complete(task_id)
            self.load_tasks()

    def edit_task(self):
        # Permite editar título y descripción de la tarea seleccionada
        task_id = self.get_selected_task_id()
        if not task_id:
            return
        task = next((t for t in self.task_manager.tasks if t["id"] == task_id), None)
        if task:
            new_title = simpledialog.askstring("Edit Task", "Edit title:", initialvalue=task["title"])
            if new_title is not None:
                new_desc = simpledialog.askstring("Edit Task", "Edit description:", initialvalue=task["description"])
                self.task_manager.edit_task(task_id, new_title, new_desc or "")
                self.load_tasks()

    def show_description(self, event):
        # Muestra la descripción de la tarea seleccionada en el text widget
        selection = self.task_listbox.curselection()
        if not selection:
            self.description_text.config(state=tk.NORMAL)
            self.description_text.delete("1.0", tk.END)
            self.description_text.config(state=tk.DISABLED)
            return

        task_str = self.task_listbox.get(selection[0])
        task_id = int(task_str.split(']')[0][1:])
        task = next((t for t in self.task_manager.tasks if t["id"] == task_id), None)

        if task:
            self.description_text.config(state=tk.NORMAL)
            self.description_text.delete("1.0", tk.END)
            self.description_text.insert(tk.END, task["description"])
            self.description_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerGUI(root)
    root.mainloop()
