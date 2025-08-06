from pymongo import MongoClient
from bson.objectid import ObjectId

class Employee:
    def __init__(self, name, employee_id):
        self.name = name
        self.employee_id = employee_id

class Manager(Employee):
    def __init__(self, name, employee_id):
        super().__init__(name, employee_id)
        self.team = []

    def add_employee(self, employee):
        self.team.append(employee)

class Task:
    def __init__(self, title, description, assigned_to):
        self.title = title
        self.description = description
        self.assigned_to = assigned_to
        self.completed = False

    def complete_task(self):
        self.completed = True

class Project:
    def __init__(self, name):
        self.name = name
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

class TaskManager:
    def __init__(self, db_uri, db_name):
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        self.tasks_collection = self.db['tasks']

    def add_task(self, task):
        task_data = {
            'title': task.title,
            'description': task.description,
            'assigned_to': task.assigned_to,
            'completed': task.completed
        }
        result = self.tasks_collection.insert_one(task_data)
        return str(result.inserted_id)

    def get_tasks(self):
        return list(self.tasks_collection.find())

    def complete_task(self, task_id):
        self.tasks_collection.update_one(
            {'_id': ObjectId(task_id)},
            {'$set': {'completed': True}}
        )
