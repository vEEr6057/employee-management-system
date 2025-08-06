#!/usr/bin/env python3
"""
Database Migration Script for Employee Management System

This script migrates data from the existing employee_task_db database
to match the updated backend structure.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import pymongo
from pymongo import MongoClient
from bson import ObjectId
import bcrypt

class DatabaseMigration:
    def __init__(self, mongo_uri: str = "mongodb://localhost:27017/"):
        self.mongo_uri = mongo_uri
        self.client = MongoClient(mongo_uri)
        self.existing_db = self.client["employee_task_db"]
        self.backup_db = self.client["employee_task_db_backup"]
        
    def examine_existing_database(self) -> Dict[str, Any]:
        """Examine the structure of the existing database."""
        print("Examining existing database structure...")
        
        examination_report = {
            "database_name": "employee_task_db",
            "collections": {},
            "total_documents": 0
        }
        
        # Get all collections
        collections = self.existing_db.list_collection_names()
        print(f"Found collections: {collections}")
        
        for collection_name in collections:
            collection = self.existing_db[collection_name]
            doc_count = collection.count_documents({})
            
            # Sample a few documents to understand structure
            sample_docs = list(collection.find().limit(3))
            
            examination_report["collections"][collection_name] = {
                "document_count": doc_count,
                "sample_documents": []
            }
            
            # Remove _id from sample docs for cleaner output
            for doc in sample_docs:
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])
                examination_report["collections"][collection_name]["sample_documents"].append(doc)
            
            examination_report["total_documents"] += doc_count
            
            print(f"Collection '{collection_name}': {doc_count} documents")
            if sample_docs:
                print(f"  Sample structure: {list(sample_docs[0].keys())}")
        
        return examination_report
    
    def backup_existing_data(self) -> bool:
        """Create a backup of existing data before migration."""
        print("Creating backup of existing data...")
        
        try:
            # Drop backup database if it exists
            self.client.drop_database("employee_task_db_backup")
            
            collections = self.existing_db.list_collection_names()
            for collection_name in collections:
                source_collection = self.existing_db[collection_name]
                backup_collection = self.backup_db[collection_name]
                
                # Copy all documents
                documents = list(source_collection.find())
                if documents:
                    backup_collection.insert_many(documents)
                    print(f"Backed up {len(documents)} documents from '{collection_name}'")
            
            print("Backup completed successfully!")
            return True
            
        except Exception as e:
            print(f"Error during backup: {e}")
            return False
    
    def migrate_auth_users_to_employees(self) -> bool:
        """Migrate auth_users collection to employees collection structure."""
        print("Migrating auth_users to employees structure...")
        
        try:
            auth_users = self.existing_db["auth_users"]
            employees = self.existing_db["employees"]
            
            # Check if auth_users collection exists
            if "auth_users" not in self.existing_db.list_collection_names():
                print("No auth_users collection found, skipping migration.")
                return True
            
            auth_users_docs = list(auth_users.find())
            print(f"Found {len(auth_users_docs)} documents in auth_users")
            
            for auth_user in auth_users_docs:
                # Check if this user already exists in employees
                existing_employee = employees.find_one({
                    "$or": [
                        {"email": auth_user.get("email")},
                        {"employee_id": auth_user.get("user_id", auth_user.get("id"))}
                    ]
                })
                
                if existing_employee:
                    print(f"Employee {auth_user.get('email')} already exists, skipping...")
                    continue
                
                # Map auth_user fields to employee structure
                employee_doc = {
                    "employee_id": auth_user.get("user_id", auth_user.get("id", self._get_next_employee_id())),
                    "name": auth_user.get("name", auth_user.get("username", "Unknown")),
                    "email": auth_user.get("email"),
                    "role": auth_user.get("role", "Employee"),
                    "created_at": auth_user.get("created_at", datetime.now().isoformat())
                }
                
                # Handle password hash
                if "password_hash" in auth_user:
                    employee_doc["password_hash"] = auth_user["password_hash"]
                elif "password" in auth_user:
                    # If plain password exists, hash it
                    employee_doc["password_hash"] = bcrypt.hashpw(
                        auth_user["password"].encode('utf-8'), 
                        bcrypt.gensalt()
                    )
                else:
                    # Create a default password that must be changed
                    employee_doc["password_hash"] = bcrypt.hashpw(
                        "changeme".encode('utf-8'), 
                        bcrypt.gensalt()
                    )
                
                employees.insert_one(employee_doc)
                print(f"Migrated user: {employee_doc['email']}")
            
            print("Auth users migration completed!")
            return True
            
        except Exception as e:
            print(f"Error migrating auth_users: {e}")
            return False
    
    def ensure_required_collections(self) -> bool:
        """Ensure all required collections exist."""
        print("Ensuring required collections exist...")
        
        required_collections = ["employees", "tasks", "projects"]
        existing_collections = self.existing_db.list_collection_names()
        
        for collection_name in required_collections:
            if collection_name not in existing_collections:
                print(f"Creating missing collection: {collection_name}")
                self.existing_db.create_collection(collection_name)
            else:
                print(f"Collection '{collection_name}' already exists")
        
        return True
    
    def update_task_structure(self) -> bool:
        """Update tasks to match expected structure."""
        print("Updating task structure...")
        
        try:
            tasks_collection = self.existing_db["tasks"]
            tasks = list(tasks_collection.find())
            
            for task in tasks:
                updates = {}
                
                # Ensure required fields exist
                if "time_logs" not in task:
                    updates["time_logs"] = []
                
                if "created_at" not in task:
                    updates["created_at"] = datetime.now().isoformat()
                
                if "updated_at" not in task:
                    updates["updated_at"] = datetime.now().isoformat()
                
                if "priority" not in task:
                    updates["priority"] = "Medium"
                
                if "status" not in task:
                    updates["status"] = "Pending"
                
                # Apply updates if any
                if updates:
                    tasks_collection.update_one(
                        {"_id": task["_id"]},
                        {"$set": updates}
                    )
                    print(f"Updated task: {task.get('title', task.get('_id'))}")
            
            print("Task structure update completed!")
            return True
            
        except Exception as e:
            print(f"Error updating task structure: {e}")
            return False
    
    def _get_next_employee_id(self) -> int:
        """Get the next available employee ID."""
        employees = self.existing_db["employees"]
        last_employee = employees.find_one({}, sort=[("employee_id", -1)])
        return (last_employee["employee_id"] + 1) if last_employee else 1
    
    def run_migration(self) -> bool:
        """Run the complete migration process."""
        print("Starting database migration...")
        print("=" * 50)
        
        # Step 1: Examine existing database
        examination_report = self.examine_existing_database()
        
        # Step 2: Create backup
        if not self.backup_existing_data():
            print("Failed to create backup. Aborting migration.")
            return False
        
        # Step 3: Ensure required collections exist
        if not self.ensure_required_collections():
            print("Failed to ensure required collections. Aborting migration.")
            return False
        
        # Step 4: Migrate auth_users to employees
        if not self.migrate_auth_users_to_employees():
            print("Failed to migrate auth_users. Continuing with other steps...")
        
        # Step 5: Update task structure
        if not self.update_task_structure():
            print("Failed to update task structure. Continuing...")
        
        print("=" * 50)
        print("Migration completed!")
        
        # Final examination
        print("\nFinal database state:")
        final_report = self.examine_existing_database()
        
        return True

def main():
    """Main function to run the migration."""
    try:
        migration = DatabaseMigration()
        success = migration.run_migration()
        
        if success:
            print("\n✅ Migration completed successfully!")
            print("You can now update your backend to connect to 'employee_task_db'")
        else:
            print("\n❌ Migration failed!")
            
    except Exception as e:
        print(f"Migration error: {e}")

if __name__ == "__main__":
    main()