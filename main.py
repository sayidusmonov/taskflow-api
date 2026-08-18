from fastapi import FastAPI, HTTPException, Depends 
from pydantic import BaseModel 
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session 
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI()
security = HTTPBearer()

DATABASE_URL = "sqlite:///./tasks.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key-change-this-later"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
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
    owner = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Habit(BaseModel): 
    name: str

class HabitDB(Base): 
    __tablename__ = "habits"
    id = Column(Integer, primary_key=True) 
    name = Column(String)
    owner = Column(String)
    current_streak = Column(Integer, default=0)
    last_completed = Column(String, default=None, nullable=True)

class User(BaseModel):
    username: str
    password: str

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)

def hash_password(password: str):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_db(): 
    db =  SessionLocal()
    try: 
        yield db 
    finally: 
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

Base.metadata.create_all(bind=engine)

@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    return db.query(TaskDB).filter(TaskDB.owner == current_user.username).all()

@app.get("/habits")
def get_habits(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    return db.query(HabitDB).filter(HabitDB.owner == current_user.username).all()

@app.post("/tasks")
def create_task(task: Task, db:  Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    new_task = TaskDB(id=task.id, title= task.title, completed=task.completed, owner=current_user.username)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.post("/habits")
def create_habit(habit: Habit, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)): 
    new_habit =HabitDB(name=habit.name, owner=current_user.username, current_streak=0, last_completed=None)
    db.add(new_habit)
    db.commit()
    db.refresh(new_habit)
    return new_habit

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)): 
    task = db.query(TaskDB).filter(TaskDB.id == task_id, TaskDB.owner == current_user.username).first()
    if task is None: 
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return{"message": f"Task{task_id} deleted"}

@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: Task, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)): 
    task = db.query(TaskDB).filter(TaskDB.id == task_id, TaskDB.owner == current_user.username).first()
    if task is None: 
        raise HTTPException(status_code=404, detail="Task not found")
    task.title = updated_task.title 
    task.completed = updated_task.completed
    db.commit()
    db.refresh(task)
    return task

@app.post("/register")
def register(user: User, db: Session = Depends(get_db)):
    hashed = hash_password(user.password)
    new_user = UserDB(username=user.username, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}


@app.post("/login")
def login(user: User, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    if db_user is None: 
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not verify_password(user.password, db_user.hashed_password): 
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
