# TaskFlow API

A task management REST API built with FastAPI, featuring JWT authentication and per-user task ownership.

## Features

- Full CRUD for tasks (Create, Read, Update, Delete)
- User registration and login with hashed passwords (bcrypt)
- JWT token-based authentication
- Tasks are private — each user only sees their own
- SQLite database with SQLAlchemy ORM

## Tech Stack

- **FastAPI** — web framework
- **SQLAlchemy** — database ORM
- **SQLite** — database
- **Passlib (bcrypt)** — password hashing
- **python-jose** — JWT token creation/verification

## Getting Started

1. Clone the repo and set up a virtual environment:
```bash
   python3 -m venv venv
   source venv/bin/activate
```

2. Install dependencies:
```bash
   pip install fastapi uvicorn sqlalchemy passlib bcrypt "python-jose[cryptography]" python-multipart
```

3. Run the server:
```bash
   uvicorn main:app --reload
```

4. Open the interactive API docs:
http://127.0.0.1:8000/docs
5. ## API Endpoints

| Method | Endpoint             | Description                  | Auth Required |
|--------|-----------------------|-------------------------------|----------------|
| POST   | `/register`           | Create a new user account     | No             |
| POST   | `/login`               | Log in, receive a JWT token   | No             |
| GET    | `/tasks`               | Get all of your tasks         | Yes            |
| POST   | `/tasks`               | Create a new task             | Yes            |
| PUT    | `/tasks/{task_id}`     | Update a task                 | Yes            |
| DELETE | `/tasks/{task_id}`     | Delete a task                 | Yes            |

## Author

Built by Sayid Usmonov as a learning project — full CRUD, database integration, and authentication built from scratch.
