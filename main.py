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
def create_tasks(task: Task):
    tasks.append(task)
    return task 
