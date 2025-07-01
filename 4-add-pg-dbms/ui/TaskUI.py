from datetime import datetime
import logging
from db.connection import TaskManagerException


class TaskUI:
    """User interface for the task manager"""
    def __init__(self, service):
        self.service = service
    
    def display_task(self, task):
        """Display a single task"""
        print(f"ID: {task.task_id}")
        print(f"Title: {task.title}")
        print(f"Description: {task.description}")
        print(f"Status: {task.status}")
        print(f"Created: {task.created_date}")
        print("-" * 40)
    
    def display_tasks(self, tasks):
        """Display a list of tasks"""
        if not tasks:
            print("No tasks found.")
            return
        
        print("\n" + "=" * 80)
        print(f"{'ID':<5} {'TITLE':<25} {'STATUS':<10} {'CREATED DATE':<20} {'DESCRIPTION':<30}")
        print("-" * 80)
        
        for task in tasks:
            created_str = task.created_date.strftime("%Y-%m-%d %H:%M:%S") if isinstance(task.created_date, datetime) else str(task.created_date)
            print(f"{task.task_id:<5} {task.title[:23]:<25} {task.status:<10} "
                  f"{created_str:<20} {task.description[:28]:<30}")
        
        print("=" * 80 + "\n")
    
    def display_statistics(self):
        """Display task statistics"""
        try:
            stats = self.service.get_statistics()
            print("\n" + "=" * 40)
            print("TASK STATISTICS")
            print("-" * 40)
            print(f"Total Tasks: {stats.get('total_tasks', 0)}")
            print(f"Pending Tasks: {stats.get('pending_tasks', 0)}")
            print(f"Completed Tasks: {stats.get('completed_tasks', 0)}")
            print(f"Tasks Created Today: {stats.get('tasks_today', 0)}")
            print("=" * 40 + "\n")
        except TaskManagerException as e:
            print(f"Error getting statistics: {str(e)}")
    
    def add_task_ui(self):
        """UI for adding a task"""
        print("\n== Add New Task ==")
        title = input("Enter task title: ")
        description = input("Enter task description: ")
        
        try:
            task = self.service.add_task(title, description)
            print(f"Task '{task.title}' added successfully with ID {task.task_id}!")
        except TaskManagerException as e:
            print(f"Error: {str(e)}")
    
    def list_tasks_ui(self):
        """UI for listing tasks"""
        try:
            tasks = self.service.list_tasks()
            self.display_tasks(tasks)
        except TaskManagerException as e:
            print(f"Error: {str(e)}")
    
    def mark_complete_ui(self):
        """UI for marking a task as complete"""
        task_id = input("Enter task ID to mark as complete: ")
        
        try:
            task = self.service.mark_complete(task_id)
            print(f"Task '{task.title}' marked as completed!")
        except TaskManagerException as e:
            print(f"Error: {str(e)}")
    
    def delete_task_ui(self):
        """UI for deleting a task"""
        task_id = input("Enter task ID to delete: ")
        
        try:
            task = self.service.delete_task(task_id)
            print(f"Task '{task.title}' deleted successfully!")
        except TaskManagerException as e:
            print(f"Error: {str(e)}")
    
    def search_tasks_ui(self):
        """UI for searching tasks"""
        keyword = input("Enter search keyword: ")
        
        try:
            tasks = self.service.search_tasks(keyword)
            if tasks:
                print(f"Found {len(tasks)} matching tasks:")
                self.display_tasks(tasks)
            else:
                print(f"No tasks found matching '{keyword}'")
        except TaskManagerException as e:
            print(f"Error: {str(e)}")
    
    def run(self):
        """Main UI loop"""
        while True:
            print("\nTASK MANAGER (PostgreSQL)")
            print("1. Add Task")
            print("2. List Tasks")
            print("3. Mark Task as Complete")
            print("4. Delete Task")
            print("5. Search Tasks")
            print("6. View Statistics")
            print("7. Exit")
            
            choice = input("Enter your choice (1-7): ")
            
            try:
                if choice == "1":
                    self.add_task_ui()
                
                elif choice == "2":
                    self.list_tasks_ui()
                
                elif choice == "3":
                    self.mark_complete_ui()
                
                elif choice == "4":
                    self.delete_task_ui()
                
                elif choice == "5":
                    self.search_tasks_ui()
                
                elif choice == "6":
                    self.display_statistics()
                
                elif choice == "7":
                    print("Exiting Task Manager. Goodbye!")
                    break
                
                else:
                    print("Invalid choice. Please try again.")
            
            except Exception as e:
                logging.error(f"Unexpected error: {str(e)}")
                print(f"An unexpected error occurred. Please try again.")