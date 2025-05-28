import os
import json
import logging
from datetime import datetime


# Configure logging
logging.basicConfig(
    filename='task_manager.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.file_name = "tasks.json"
        self.load_tasks()
    
    def load_tasks(self):
        if os.path.exists(self.file_name):
            try:
                with open(self.file_name, "r") as file:
                    self.tasks = json.load(file)
                
                logging.info(f"Loaded {len(self.tasks)} tasks from {self.file_name}")
            except Exception as e:
                # Log the error and start with an empty task list

                logging.error(f"Error loading task data from {self.file_name}: {str(e)}")
                self.tasks = []
        else:
            logging.info(f"No existing task file found at {self.file_name}")
    
    def save_tasks(self):
        try:
            with open(self.file_name, "w") as file:
                json.dump(self.tasks, file)
            logging.info(f"Saved {len(self.tasks)} tasks to {self.file_name}")
        except Exception as e:
            logging.error(f"Error saving task data to {self.file_name}: {str(e)}")

    def get_next_id(self):
        if not self.tasks:
            return 1
        return max(task["id"] for task in self.tasks) + 1
    
    def add_task(self, title, description):
        task = {
            "id": self.get_next_id(),
            "title": title,
            "description": description,
            "status": "Pending",
            "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.tasks.append(task)
        self.save_tasks()
        logging.info(f"Task '{title}' added successfully!")
    
    def list_tasks(self):
        if not self.tasks:
            logging.error("No tasks found.")
            return
        
        print("\n" + "=" * 80)
        print(f"{'ID':<5} {'TITLE':<20} {'STATUS':<10} {'CREATED DATE':<20} {'DESCRIPTION':<30}")
        print("-" * 80)
        
        for task in self.tasks:
            print(f"{task['id']:<5} {task['title'][:18]:<20} {task['status']:<10} {task['created_date']:<20} {task['description'][:28]:<30}")
        
        print("=" * 80 + "\n")
    
    def mark_complete(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                task["status"] = "Completed"
                self.save_tasks()
                logging.info(f"Task '{task['title']}' marked as completed!")
                return
        logging.error(f"Task with ID {task_id} not found.")
    
    def delete_task(self, task_id):
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                removed = self.tasks.pop(i)
                self.save_tasks()
                logging.info(f"Task '{removed['title']}' deleted successfully!")
                return
        logging.error(f"Task with ID {task_id} not found.")


def main():
    task_manager = TaskManager()
    
    while True:
        print("\nTASK MANAGER")
        print("1. Add Task")
        print("2. List Tasks")
        print("3. Mark Task as Complete")
        print("4. Delete Task")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == "1":
            title = input("Enter task title: ")
            description = input("Enter task description: ")
            task_manager.add_task(title, description)
        
        elif choice == "2":
            task_manager.list_tasks()
        
        elif choice == "3":
            task_id = int(input("Enter task ID to mark as complete: "))
            task_manager.mark_complete(task_id)
        
        elif choice == "4":
            task_id = int(input("Enter task ID to delete: "))
            task_manager.delete_task(task_id)
        
        elif choice == "5":
            print("Exiting Task Manager. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()