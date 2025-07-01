from app.config import load_environment
from db.connection import DatabaseConnectionError
from repositories.TaskRepository import TaskRepository
from services.TaskService import TaskService
from ui.TaskUI import TaskUI
import logging
import db.init_db as init_db


def main():
    try:
        init_db.init_database()
        load_environment()
        repository = TaskRepository()
        service = TaskService(repository)
        ui = TaskUI(service)
        ui.run()
    except DatabaseConnectionError as e:
        print(f"Database connection failed: {str(e)}")
    except Exception as e:
        print("A critical error occurred. Check logs.")
        logging.error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
