import os
import logging
import psycopg2
from contextlib import contextmanager
from dotenv import load_dotenv

class TaskManagerException(Exception):
    """Custom exception for TaskManager operations"""
    pass

class DatabaseConnectionError(TaskManagerException):
    """Exception for database connection issues"""
    pass

class DatabaseManager:
    """Database connection and management class"""
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        self.connection_params = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD')
        }

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            yield conn
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            logging.error(f"Database error: {str(e)}")
            raise DatabaseConnectionError(f"Database connection failed: {str(e)}")
        finally:
            if conn:
                conn.close()
