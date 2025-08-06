from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from backend import TaskManager, Employee, Manager, Task, Project

app = FastAPI(title="Employee Management System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize TaskManager
task_manager = TaskManager()
security = HTTPBearer()

# Pydantic models
class EmployeeCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "Employee"

class EmployeeLogin(BaseModel):
    email: str
    password: str

class TaskCreate(BaseModel):
    title: str
    description: str
    assigned_to: int
    priority: str = "Medium"
    project_id: Optional[int] = None

class TaskUpdate(BaseModel):
    status: str

class TimeLogCreate(BaseModel):
    hours: float
    description: str = ""

class ProjectCreate(BaseModel):
    name: str
    description: str

class TaskProjectUpdate(BaseModel):
    project_id: Optional[int]

# Auth dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = task_manager.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

# Manager role dependency
async def get_current_manager(current_user = Depends(get_current_user)):
    if current_user["role"] != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )
    return current_user

# Authentication endpoints
@app.post("/auth/register")
async def register_employee(employee_data: EmployeeCreate):
    employee_id = task_manager.get_next_employee_id()
    
    if employee_data.role == "Manager":
        employee = Manager(employee_id, employee_data.name, employee_data.email, employee_data.password)
    else:
        employee = Employee(employee_id, employee_data.name, employee_data.email, employee_data.password)
    
    if task_manager.add_employee(employee):
        return {"message": "Employee registered successfully", "employee_id": employee_id}
    else:
        raise HTTPException(status_code=400, detail="Employee already exists")

@app.post("/auth/login")
async def login_employee(login_data: EmployeeLogin):
    auth_result = task_manager.authenticate_employee(login_data.email, login_data.password)
    if auth_result:
        return auth_result
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# Employee endpoints
@app.get("/employees/me")
async def get_current_employee_info(current_user = Depends(get_current_user)):
    employee = task_manager.get_employee_by_id(current_user["employee_id"])
    if employee:
        return employee
    else:
        raise HTTPException(status_code=404, detail="Employee not found")

@app.get("/employees")
async def get_all_employees(current_user = Depends(get_current_manager)):
    return task_manager.get_all_employees()

@app.get("/employees/{employee_id}")
async def get_employee(employee_id: int, current_user = Depends(get_current_manager)):
    employee = task_manager.get_employee_by_id(employee_id)
    if employee:
        return employee
    else:
        raise HTTPException(status_code=404, detail="Employee not found")

# Task endpoints
@app.post("/tasks")
async def create_task(task_data: TaskCreate, current_user = Depends(get_current_manager)):
    task_id = task_manager.get_next_task_id()
    task = Task(
        task_id=task_id,
        title=task_data.title,
        description=task_data.description,
        assigned_to=task_data.assigned_to,
        priority=task_data.priority,
        project_id=task_data.project_id
    )
    
    if task_manager.add_task(task):
        return {"message": "Task created successfully", "task_id": task_id}
    else:
        raise HTTPException(status_code=400, detail="Task already exists")

@app.get("/tasks")
async def get_tasks(current_user = Depends(get_current_user)):
    if current_user["role"] == "Manager":
        return task_manager.get_all_tasks()
    else:
        return task_manager.get_tasks_by_employee(current_user["employee_id"])

@app.get("/tasks/{task_id}")
async def get_task(task_id: int, current_user = Depends(get_current_user)):
    task = task_manager.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if employee can access this task
    if current_user["role"] != "Manager" and task["assigned_to"] != current_user["employee_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return task

@app.put("/tasks/{task_id}/status")
async def update_task_status(task_id: int, task_update: TaskUpdate, current_user = Depends(get_current_user)):
    task = task_manager.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if employee can update this task
    if current_user["role"] != "Manager" and task["assigned_to"] != current_user["employee_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if task_manager.update_task_status(task_id, task_update.status):
        return {"message": "Task status updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to update task status")

@app.post("/tasks/{task_id}/time-log")
async def add_time_log(task_id: int, time_log: TimeLogCreate, current_user = Depends(get_current_user)):
    task = task_manager.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if employee can log time for this task
    if current_user["role"] != "Manager" and task["assigned_to"] != current_user["employee_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if task_manager.add_time_log(task_id, current_user["employee_id"], time_log.hours, time_log.description):
        return {"message": "Time log added successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to add time log")

@app.get("/tasks/{task_id}/time-logs")
async def get_task_time_logs(task_id: int, current_user = Depends(get_current_user)):
    task = task_manager.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if employee can access this task
    if current_user["role"] != "Manager" and task["assigned_to"] != current_user["employee_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return task.get("time_logs", [])

@app.get("/employees/{employee_id}/time-logs")
async def get_employee_time_logs(employee_id: int, current_user = Depends(get_current_user)):
    # Employees can only see their own logs, managers can see all
    if current_user["role"] != "Manager" and current_user["employee_id"] != employee_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return task_manager.get_employee_time_logs(employee_id)

# Project endpoints
@app.post("/projects")
async def create_project(project_data: ProjectCreate, current_user = Depends(get_current_manager)):
    project_id = task_manager.get_next_project_id()
    project = Project(
        project_id=project_id,
        name=project_data.name,
        description=project_data.description,
        created_by=current_user["employee_id"]
    )
    
    if task_manager.add_project(project):
        return {"message": "Project created successfully", "project_id": project_id}
    else:
        raise HTTPException(status_code=400, detail="Project already exists")

@app.get("/projects")
async def get_all_projects(current_user = Depends(get_current_user)):
    return task_manager.get_all_projects()

@app.get("/projects/{project_id}")
async def get_project(project_id: int, current_user = Depends(get_current_user)):
    project = task_manager.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.get("/projects/{project_id}/tasks")
async def get_project_tasks(project_id: int, current_user = Depends(get_current_user)):
    project = task_manager.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    tasks = task_manager.get_tasks_by_project(project_id)
    
    # Filter tasks for employees (only their assigned tasks)
    if current_user["role"] != "Manager":
        tasks = [task for task in tasks if task["assigned_to"] == current_user["employee_id"]]
    
    return tasks

@app.put("/tasks/{task_id}/project")
async def update_task_project(task_id: int, update_data: TaskProjectUpdate, current_user = Depends(get_current_manager)):
    task = task_manager.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Validate project exists if project_id is provided
    if update_data.project_id is not None:
        project = task_manager.get_project_by_id(update_data.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
    
    if task_manager.update_task_project(task_id, update_data.project_id):
        return {"message": "Task project updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to update task project")

@app.get("/tasks/without-project")
async def get_tasks_without_project(current_user = Depends(get_current_manager)):
    return task_manager.get_tasks_without_project()

# Dashboard endpoints
@app.get("/dashboard/stats")
async def get_dashboard_stats(current_user = Depends(get_current_user)):
    if current_user["role"] == "Manager":
        return task_manager.get_dashboard_stats()
    else:
        return task_manager.get_dashboard_stats(current_user["employee_id"])

@app.get("/")
async def root():
    return {"message": "Employee Management System API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
