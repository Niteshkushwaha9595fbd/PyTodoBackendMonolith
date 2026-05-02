import mysql.connector
import uvicorn
import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MySQL connection details
db_config = {
    "host": os.getenv("DB_HOST", "todo_mysql"),
    "user": os.getenv("DB_USER", "todouser"),
    "password": os.getenv("DB_PASSWORD", "todopass"),
    "database": os.getenv("DB_NAME", "tododb"),
    "port": int(os.getenv("DB_PORT", "3306"))
}

app = FastAPI()

# Configure CORSMiddleware to allow all origins (disable CORS for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows all origins (use '*' for development only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the Task model
class Task(BaseModel):
    title: str
    description: str

# Create a table for tasks (You can run this once outside of the app)
@app.get("/api")
def create_tasks_table():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                status ENUM('pending', 'completed') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating table: {e}")
    return "Table Created... Todos API Ready"

# List all tasks
@app.get("/api/tasks")
def get_tasks():
    tasks = []
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM todos")
        for row in cursor.fetchall():
            tasks.append(row)
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error fetching tasks: {e}")
    return tasks

# Retrieve a single task by ID
@app.get("/api/tasks/{task_id}")
def get_task(task_id: int):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM todos WHERE id = %s", (task_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            return row
        return {"message": "Task not found"}
    except Exception as e:
        print(f"Error fetching task: {e}")
        return {"message": "Error fetching task"}

# Create a new task
@app.post("/api/tasks")
def create_task(task: Task):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO todos (title, description) VALUES (%s, %s)", (task.title, task.description))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Task created", "task": task}
    except Exception as e:
        print(f"Error creating task: {e}")
        return {"message": "Error creating task"}

# Update an existing task by ID
@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, updated_task: Task):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("UPDATE todos SET title = %s, description = %s WHERE id = %s", (updated_task.title, updated_task.description, task_id))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Task updated"}
    except Exception as e:
        print(f"Error updating task: {e}")
        return {"message": "Error updating task"}

# Delete a task by ID
@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM todos WHERE id = %s", (task_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Task deleted"}
    except Exception as e:
        print(f"Error deleting task: {e}")
        return {"message": "Error deleting task"}

if __name__ == "__main__":
    create_tasks_table()
    uvicorn.run(app, host="0.0.0.0", port=8000)
