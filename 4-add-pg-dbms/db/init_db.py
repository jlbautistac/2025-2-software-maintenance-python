import logging
from db.connection import DatabaseManager, DatabaseConnectionError


def init_database():
    """Initialize the database schema if not already present"""
    db_manager = DatabaseManager()
    try:
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(50) NOT NULL,
                        description TEXT NOT NULL,
                        status VARCHAR(20) DEFAULT 'Pending',
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_tasks_title 
                    ON tasks USING GIN (to_tsvector('english', title))
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_tasks_description 
                    ON tasks USING GIN (to_tsvector('english', description))
                """)
                conn.commit()
                logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize database: {str(e)}")
        raise DatabaseConnectionError(f"Failed to initialize database: {str(e)}")
