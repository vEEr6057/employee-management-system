from datetime import datetime
from typing import Optional, List, Dict, Any
import bcrypt
from pymongo import MongoClient
from bson import ObjectId
import jwt
from datetime import datetime, timedelta

class Employee:
    def __init__(self, employee_id: int, name: str, email: str, password: str, role: str = "Employee"):
        self.employee_id = employee_id
        self.name = name
        self.email = email
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.role = role
        self.created_at = datetime.now().isoformat()

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)

    def to_dict(self):
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at
        }

class Task:
    def __init__(self, task_id: int, title: str, description: str, assigned_to: int, 
                 priority: str = "Medium", status: str = "Pending", project_id: Optional[int] = None):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.assigned_to = assigned_to
        self.priority = priority
        self.status = status
        self.project_id = project_id
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.time_logs = []

    def update_status(self, status: str):
        self.status = status
        self.updated_at = datetime.now().isoformat()

    def add_time_log(self, employee_id: int, hours: float, description: str = ""):
        time_log = {
            "employee_id": employee_id,
            "hours": hours,
            "description": description,
            "logged_at": datetime.now().isoformat()
        }
        self.time_logs.append(time_log)
        self.updated_at = datetime.now().isoformat()

    def get_total_hours(self) -> float:
        return sum(log["hours"] for log in self.time_logs)

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "assigned_to": self.assigned_to,
            "priority": self.priority,
            "status": self.status,
            "project_id": self.project_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "time_logs": self.time_logs,
            "total_hours": self.get_total_hours()
        }

class Project:
    def __init__(self, project_id: int, name: str, description: str, created_by: int):
        self.project_id = project_id
        self.name = name
        self.description = description
        self.created_by = created_by
        self.created_at = datetime.now().isoformat()

    def to_dict(self):
        return {
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "created_by": self.created_by,
            "created_at": self.created_at
        }

class Manager(Employee):
    def __init__(self, employee_id: int, name: str, email: str, password: str):
        super().__init__(employee_id, name, email, password, role="Manager")

class TaskManager:
    def __init__(self, mongo_uri: str = "mongodb://localhost:27017/", db_name: str = "employee_management"):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.employees_collection = self.db.employees
        self.tasks_collection = self.db.tasks
        self.projects_collection = self.db.projects
        self.SECRET_KEY = "your-secret-key-here"

    # Employee Management
    def add_employee(self, employee: Employee) -> bool:
        try:
            if self.employees_collection.find_one({"employee_id": employee.employee_id}):
                return False
            
            employee_data = employee.to_dict()
            employee_data["password_hash"] = employee.password_hash
            self.employees_collection.insert_one(employee_data)
            return True
        except Exception as e:
            print(f"Error adding employee: {e}")
            return False

    def authenticate_employee(self, email: str, password: str) -> Optional[Dict]:
        try:
            employee_data = self.employees_collection.find_one({"email": email})
            if employee_data and bcrypt.checkpw(password.encode('utf-8'), employee_data["password_hash"]):
                token = jwt.encode({
                    "employee_id": employee_data["employee_id"],
                    "email": employee_data["email"],
                    "role": employee_data["role"],
                    "exp": datetime.utcnow() + timedelta(hours=24)
                }, self.SECRET_KEY, algorithm="HS256")
                
                return {
                    "employee_id": employee_data["employee_id"],
                    "name": employee_data["name"],
                    "email": employee_data["email"],
                    "role": employee_data["role"],
                    "token": token
                }
            return None
        except Exception as e:
            print(f"Error authenticating employee: {e}")
            return None

    def verify_token(self, token: str) -> Optional[Dict]:
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def get_employee_by_id(self, employee_id: int) -> Optional[Dict]:
        try:
            employee = self.employees_collection.find_one({"employee_id": employee_id})
            if employee:
                employee.pop("password_hash", None)
                employee.pop("_id", None)
            return employee
        except Exception as e:
            print(f"Error getting employee: {e}")
            return None

    def get_all_employees(self) -> List[Dict]:
        try:
            employees = list(self.employees_collection.find({}, {"password_hash": 0, "_id": 0}))
            return employees
        except Exception as e:
            print(f"Error getting employees: {e}")
            return []

    # Task Management
    def add_task(self, task: Task) -> bool:
        try:
            if self.tasks_collection.find_one({"task_id": task.task_id}):
                return False
            
            self.tasks_collection.insert_one(task.to_dict())
            return True
        except Exception as e:
            print(f"Error adding task: {e}")
            return False

    def get_task_by_id(self, task_id: int) -> Optional[Dict]:
        try:
            task = self.tasks_collection.find_one({"task_id": task_id}, {"_id": 0})
            return task
        except Exception as e:
            print(f"Error getting task: {e}")
            return None

    def get_tasks_by_employee(self, employee_id: int) -> List[Dict]:
        try:
            tasks = list(self.tasks_collection.find({"assigned_to": employee_id}, {"_id": 0}))
            return tasks
        except Exception as e:
            print(f"Error getting tasks for employee: {e}")
            return []

    def get_all_tasks(self) -> List[Dict]:
        try:
            tasks = list(self.tasks_collection.find({}, {"_id": 0}))
            return tasks
        except Exception as e:
            print(f"Error getting all tasks: {e}")
            return []

    def update_task_status(self, task_id: int, status: str) -> bool:
        try:
            result = self.tasks_collection.update_one(
                {"task_id": task_id},
                {"$set": {"status": status, "updated_at": datetime.now().isoformat()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating task status: {e}")
            return False

    def add_time_log(self, task_id: int, employee_id: int, hours: float, description: str = "") -> bool:
        try:
            time_log = {
                "employee_id": employee_id,
                "hours": hours,
                "description": description,
                "logged_at": datetime.now().isoformat()
            }
            
            result = self.tasks_collection.update_one(
                {"task_id": task_id},
                {
                    "$push": {"time_logs": time_log},
                    "$set": {"updated_at": datetime.now().isoformat()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error adding time log: {e}")
            return False

    def get_employee_time_logs(self, employee_id: int) -> List[Dict]:
        try:
            tasks = self.tasks_collection.find(
                {"time_logs.employee_id": employee_id},
                {"task_id": 1, "title": 1, "time_logs": 1, "_id": 0}
            )
            
            employee_logs = []
            for task in tasks:
                for log in task.get("time_logs", []):
                    if log["employee_id"] == employee_id:
                        log["task_id"] = task["task_id"]
                        log["task_title"] = task["title"]
                        employee_logs.append(log)
            
            return employee_logs
        except Exception as e:
            print(f"Error getting employee time logs: {e}")
            return []

    # Project Management
    def add_project(self, project: Project) -> bool:
        try:
            if self.projects_collection.find_one({"project_id": project.project_id}):
                return False
            
            self.projects_collection.insert_one(project.to_dict())
            return True
        except Exception as e:
            print(f"Error adding project: {e}")
            return False

    def get_project_by_id(self, project_id: int) -> Optional[Dict]:
        try:
            project = self.projects_collection.find_one({"project_id": project_id}, {"_id": 0})
            return project
        except Exception as e:
            print(f"Error getting project: {e}")
            return None

    def get_all_projects(self) -> List[Dict]:
        try:
            projects = list(self.projects_collection.find({}, {"_id": 0}))
            return projects
        except Exception as e:
            print(f"Error getting all projects: {e}")
            return []

    def get_tasks_by_project(self, project_id: int) -> List[Dict]:
        try:
            tasks = list(self.tasks_collection.find({"project_id": project_id}, {"_id": 0}))
            return tasks
        except Exception as e:
            print(f"Error getting tasks for project: {e}")
            return []

    def update_task_project(self, task_id: int, project_id: Optional[int]) -> bool:
        try:
            result = self.tasks_collection.update_one(
                {"task_id": task_id},
                {"$set": {"project_id": project_id, "updated_at": datetime.now().isoformat()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating task project: {e}")
            return False

    def get_tasks_without_project(self) -> List[Dict]:
        try:
            tasks = list(self.tasks_collection.find(
                {"$or": [{"project_id": None}, {"project_id": {"$exists": False}}]},
                {"_id": 0}
            ))
            return tasks
        except Exception as e:
            print(f"Error getting tasks without project: {e}")
            return []

    def get_next_project_id(self) -> int:
        try:
            last_project = self.projects_collection.find_one({}, sort=[("project_id", -1)])
            return (last_project["project_id"] + 1) if last_project else 1
        except Exception as e:
            print(f"Error getting next project ID: {e}")
            return 1

    def get_next_task_id(self) -> int:
        try:
            last_task = self.tasks_collection.find_one({}, sort=[("task_id", -1)])
            return (last_task["task_id"] + 1) if last_task else 1
        except Exception as e:
            print(f"Error getting next task ID: {e}")
            return 1

    def get_next_employee_id(self) -> int:
        try:
            last_employee = self.employees_collection.find_one({}, sort=[("employee_id", -1)])
            return (last_employee["employee_id"] + 1) if last_employee else 1
        except Exception as e:
            print(f"Error getting next employee ID: {e}")
            return 1

    # Dashboard Analytics
    def get_dashboard_stats(self, employee_id: Optional[int] = None) -> Dict:
        try:
            if employee_id:
                # Employee-specific stats
                tasks = self.get_tasks_by_employee(employee_id)
                time_logs = self.get_employee_time_logs(employee_id)
            else:
                # Manager stats (all tasks)
                tasks = self.get_all_tasks()
                time_logs = []
                for task in tasks:
                    time_logs.extend(task.get("time_logs", []))

            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t["status"] == "Completed"])
            pending_tasks = len([t for t in tasks if t["status"] == "Pending"])
            in_progress_tasks = len([t for t in tasks if t["status"] == "In Progress"])
            total_hours = sum(log["hours"] for log in time_logs)

            # Priority breakdown
            high_priority = len([t for t in tasks if t["priority"] == "High"])
            medium_priority = len([t for t in tasks if t["priority"] == "Medium"])
            low_priority = len([t for t in tasks if t["priority"] == "Low"])

            return {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "pending_tasks": pending_tasks,
                "in_progress_tasks": in_progress_tasks,
                "total_hours": round(total_hours, 2),
                "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
                "priority_breakdown": {
                    "high": high_priority,
                    "medium": medium_priority,
                    "low": low_priority
                }
            }
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {}
