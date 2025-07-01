from db.connection import TaskManagerException


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
        
        return self.repository.search_tasks(keyword.strip())
    
    def get_statistics(self):
        """Get task statistics"""
        return self.repository.get_task_statistics()