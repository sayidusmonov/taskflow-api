from fastapi import FastAPI, HTTPException 
from pydantic import BaseModel

app = FastAPI()

class Task(BaseModel):
    id: int
    title: str
    completed: bool = False

tasks = []

@app.get("/tasks")
def get_tasks(): 
    return tasks

@app.post("/tasks")
def create_task(task: Task):
    tasks.append(task)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int): 
    for t in tasks: 
        if t.id == task_id:
            tasks.remove(t)
            return{"message": f"Task {task_id} deleted"}
    raise HTTPException(status_code=404, detail="Task not found")
    
        