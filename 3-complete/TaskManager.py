import os
import json
import logging
import configparser
from datetime import datetime


# Configure logging
logging.basicConfig(
    filename='task_manager.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class TaskManagerException(Exception):
    """Custom exception for TaskManager operations"""
    pass


class TaskModel:
    """Data model for task objects"""
    def __init__(self, task_id, title, description, status="Pending", created_date=None):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.status = status
        self.created_date = created_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self):
        """Convert task to dictionary for serialization"""
        return {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_date": self.created_date
        }
    
    @classmethod
    def from_dict(cls, task_dict):
        """Create a TaskModel from a dictionary"""
        return cls(
            task_id=task_dict["id"],
            title=task_dict["title"],
            description=task_dict["description"],
            status=task_dict["status"],
            created_date=task_dict["created_date"]
        )


class TaskRepository:
    """Repository for task data storage and retrieval"""
    def __init__(self, config):
        self.config = config
        self.file_name = config.get('Storage', 'file_name', fallback='tasks.json')
        self.tasks = []
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks from file"""
        if os.path.exists(self.file_name):
            try:
                with open(self.file_name, "r") as file:
                    task_dicts = json.load(file)
                    self.tasks = [TaskModel.from_dict(task) for task in task_dicts]
                logging.info(f"Loaded {len(self.tasks)} tasks from {self.file_name}")
            except Exception as e:
                logging.error(f"Error loading task data: {str(e)}")
                self.tasks = []
        else:
            logging.info(f"No existing task file found at {self.file_name}")
    
    def save_tasks(self):
        """Save tasks to file"""
        try:
            task_dicts = [task.to_dict() for task in self.tasks]
            with open(self.file_name, "w") as file:
                json.dump(task_dicts, file, indent=2)
            logging.info(f"Saved {len(self.tasks)} tasks to {self.file_name}")
        except Exception as e:
            logging.error(f"Error saving task data: {str(e)}")
            raise TaskManagerException(f"Failed to save tasks: {str(e)}")
    
    def get_next_id(self):
        """Generate a unique task ID"""
        if not self.tasks:
            return 1
        return max(task.task_id for task in self.tasks) + 1
    
    def add_task(self, title, description):
        """Add a new task"""
        task_id = self.get_next_id()
        task = TaskModel(task_id, title, description)
        self.tasks.append(task)
        self.save_tasks()
        logging.info(f"Added task ID {task_id}: {title}")
        return task
    
    def get_all_tasks(self):
        """Return all tasks"""
        return self.tasks
    
    def find_task_by_id(self, task_id):
        """Find a task by ID"""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def update_task(self, task):
        """Update an existing task"""
        for i, existing_task in enumerate(self.tasks):
            if existing_task.task_id == task.task_id:
                self.tasks[i] = task
                self.save_tasks()
                logging.info(f"Updated task ID {task.task_id}: {task.title}")
                return True
        return False
    
    def delete_task(self, task_id):
        """Delete a task by ID"""
        for i, task in enumerate(self.tasks):
            if task.task_id == task_id:
                removed = self.tasks.pop(i)
                self.save_tasks()
                logging.info(f"Deleted task ID {task_id}: {removed.title}")
                return removed
        return None


class TaskService:
    """Business logic layer for task operations"""
    def __init__(self, repository):
        self.repository = repository
    
    def add_task(self, title, description):
        """Add a new task with validation"""
        # Validate inputs
        if not title or not title.strip():
            raise TaskManagerException("Task title cannot be empty")
        
        if len(title) > 50:
            raise TaskManagerException("Task title cannot exceed 50 characters")
        
        if not description or not description.strip():
            raise TaskManagerException("Task description cannot be empty")
        
        return self.repository.add_task(title.strip(), description.strip())
    
    def list_tasks(self):
        """Get all tasks"""
        return self.repository.get_all_tasks()
    
    def mark_complete(self, task_id):
        """Mark a task as complete"""
        try:
            task_id = int(task_id)
        except ValueError:
            raise TaskManagerException("Task ID must be a number")
        
        task = self.repository.find_task_by_id(task_id)
        if not task:
            raise TaskManagerException(f"Task with ID {task_id} not found")
        
        task.status = "Completed"
        self.repository.update_task(task)
        return task
    
    def delete_task(self, task_id):
        """Delete a task"""
        try:
            task_id = int(task_id)
        except ValueError:
            raise TaskManagerException("Task ID must be a number")
        
        task = self.repository.delete_task(task_id)
        if not task:
            raise TaskManagerException(f"Task with ID {task_id} not found")
        
        return task
    
    def search_tasks(self, keyword):
        """Search for tasks by keyword"""
        if not keyword or not keyword.strip():
            return []
        
        keyword = keyword.lower().strip()
        return [
            task for task in self.repository.get_all_tasks()
            if keyword in task.title.lower() or keyword in task.description.lower()
        ]


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
            print(f"{task.task_id:<5} {task.title[:23]:<25} {task.status:<10} "
                  f"{task.created_date:<20} {task.description[:28]:<30}")
        
        print("=" * 80 + "\n")
    
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
        tasks = self.service.list_tasks()
        self.display_tasks(tasks)
    
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
            print("\nTASK MANAGER")
            print("1. Add Task")
            print("2. List Tasks")
            print("3. Mark Task as Complete")
            print("4. Delete Task")
            print("5. Search Tasks")
            print("6. Exit")
            
            choice = input("Enter your choice (1-6): ")
            
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
                    print("Exiting Task Manager. Goodbye!")
                    break
                
                else:
                    print("Invalid choice. Please try again.")
            
            except Exception as e:
                logging.error(f"Unexpected error: {str(e)}")
                print(f"An unexpected error occurred. Please try again.")


def load_config():
    """Load configuration from file or create default"""
    config = configparser.ConfigParser()
    
    if os.path.exists('config.ini'):
        config.read('config.ini')
    else:
        # Create default configuration
        config['Storage'] = {
            'file_name': 'tasks.json'
        }
        config['UI'] = {
            'title': 'Task Manager'
        }
        
        with open('config.ini', 'w') as f:
            config.write(f)
        
        logging.info("Created default configuration file")
    
    return config


def main():
    """Main application entry point"""
    try:
        # Load configuration
        config = load_config()
        
        # Set up the application layers
        repository = TaskRepository(config)
        service = TaskService(repository)
        ui = TaskUI(service)
        
        # Start the UI
        ui.run()
    
    except Exception as e:
        logging.critical(f"Fatal error: {str(e)}")
        print(f"A critical error occurred. Please check the logs.")


if __name__ == "__main__":
    main()