from fastapi import FastAPI, HTTPException, Depends 
from pydantic import BaseModel 
from sqlalchemy import create_engine, Column, Integer, String, Boolean 
from sqlalchemy.orm import sessionmaker, declarative_base, Session 

app = FastAPI()

DATABASE_URL = "sqlite:///./tasks.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Task(BaseModel): 
    id: int 
    title: str 
    completed: bool = False 

class TaskDB(Base): 
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    completed = Column(Boolean, default=False)

def get_db(): 
    db =  SessionLocal()
    try: 
        yield db 
    finally: 
        db.close()

Base.metadata.create_all(bind=engine)

@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db)): 
    return db.query(TaskDB).all()

@app.post("/tasks")
def create_task(task: Task, db:  Session = Depends(get_db)): 
    new_task = TaskDB(id=task.id, title= task.title, completed=task.completed)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)): 
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if task is None: 
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return{"message": f"Task{task_id} deleted"}

@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: Task, db: Session = Depends(get_db)): 
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if task is None: 
        raise HTTPException(status_code=404, detail="Task not found")
    task.title = updated_task.title 
    task.completed = updated_task.completed
    db.commit()
    db.refresh(task)
    return task