import logging
from db.connection import DatabaseManager, TaskManagerException
from models.TaskModel import TaskModel
from psycopg2.extras import RealDictCursor


class TaskRepository:
    """Repository for task data storage and retrieval using PostgreSQL"""
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def add_task(self, title, description):
        """Add a new task"""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        INSERT INTO tasks (title, description) 
                        VALUES (%s, %s) 
                        RETURNING id, title, description, status, created_date
                    """, (title, description))
                    
                    task_data = cursor.fetchone()
                    conn.commit()
                    
                    task = TaskModel.from_dict(dict(task_data))
                    logging.info(f"Added task ID {task.task_id}: {title}")
                    return task
        
        except Exception as e:
            logging.error(f"Error adding task: {str(e)}")
            raise TaskManagerException(f"Failed to add task: {str(e)}")
    
    def get_all_tasks(self):
        """Return all tasks"""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT id, title, description, status, created_date 
                        FROM tasks 
                        ORDER BY created_date DESC
                    """)
                    
                    tasks_data = cursor.fetchall()
                    tasks = [TaskModel.from_dict(dict(task)) for task in tasks_data]
                    return tasks
        
        except Exception as e:
            logging.error(f"Error retrieving tasks: {str(e)}")
            raise TaskManagerException(f"Failed to retrieve tasks: {str(e)}")
    
    def find_task_by_id(self, task_id):
        """Find a task by ID"""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT id, title, description, status, created_date 
                        FROM tasks 
                        WHERE id = %s
                    """, (task_id,))
                    
                    task_data = cursor.fetchone()
                    if task_data:
                        return TaskModel.from_dict(dict(task_data))
                    return None
        
        except Exception as e:
            logging.error(f"Error finding task by ID {task_id}: {str(e)}")
            raise TaskManagerException(f"Failed to find task: {str(e)}")
    
    def update_task(self, task):
        """Update an existing task"""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE tasks 
                        SET title = %s, description = %s, status = %s 
                        WHERE id = %s
                    """, (task.title, task.description, task.status, task.task_id))
                    
                    if cursor.rowcount > 0:
                        conn.commit()
                        logging.info(f"Updated task ID {task.task_id}: {task.title}")
                        return True
                    return False
        
        except Exception as e:
            logging.error(f"Error updating task ID {task.task_id}: {str(e)}")
            raise TaskManagerException(f"Failed to update task: {str(e)}")
    
    def delete_task(self, task_id):
        """Delete a task by ID"""
        try:
            # First get the task to return it
            task = self.find_task_by_id(task_id)
            if not task:
                return None
            
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
                    
                    if cursor.rowcount > 0:
                        conn.commit()
                        logging.info(f"Deleted task ID {task_id}: {task.title}")
                        return task
                    return None
        
        except Exception as e:
            logging.error(f"Error deleting task ID {task_id}: {str(e)}")
            raise TaskManagerException(f"Failed to delete task: {str(e)}")
    
    def search_tasks(self, keyword):
        """Search for tasks using PostgreSQL full-text search"""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT id, title, description, status, created_date 
                        FROM tasks 
                        WHERE to_tsvector('english', title || ' ' || description) @@ plainto_tsquery('english', %s)
                        OR title ILIKE %s 
                        OR description ILIKE %s
                        ORDER BY created_date DESC
                    """, (keyword, f'%{keyword}%', f'%{keyword}%'))
                    
                    tasks_data = cursor.fetchall()
                    tasks = [TaskModel.from_dict(dict(task)) for task in tasks_data]
                    return tasks
        
        except Exception as e:
            logging.error(f"Error searching tasks with keyword '{keyword}': {str(e)}")
            raise TaskManagerException(f"Failed to search tasks: {str(e)}")
    
    def get_task_statistics(self):
        """Get task statistics"""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_tasks,
                            COUNT(CASE WHEN status = 'Pending' THEN 1 END) as pending_tasks,
                            COUNT(CASE WHEN status = 'Completed' THEN 1 END) as completed_tasks,
                            COUNT(CASE WHEN created_date >= CURRENT_DATE THEN 1 END) as tasks_today
                        FROM tasks
                    """)
                    
                    stats = cursor.fetchone()
                    return dict(stats) if stats else {}
        
        except Exception as e:
            logging.error(f"Error getting task statistics: {str(e)}")
            raise TaskManagerException(f"Failed to get statistics: {str(e)}")