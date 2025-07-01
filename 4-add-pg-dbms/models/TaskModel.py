from datetime import datetime


class TaskModel:
    """Data model for task objects"""
    def __init__(self, task_id, title, description, status="Pending", created_date=None):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.status = status
        self.created_date = created_date or datetime.now()
    
    def to_dict(self):
        """Convert task to dictionary for serialization"""
        return {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_date": self.created_date.strftime("%Y-%m-%d %H:%M:%S") if isinstance(self.created_date, datetime) else self.created_date
        }
    
    @classmethod
    def from_dict(cls, task_dict):
        """Create a TaskModel from a dictionary"""
        created_date = task_dict["created_date"]
        if isinstance(created_date, str):
            created_date = datetime.strptime(created_date, "%Y-%m-%d %H:%M:%S")
        
        return cls(
            task_id=task_dict["id"],
            title=task_dict["title"],
            description=task_dict["description"],
            status=task_dict["status"],
            created_date=created_date
        )