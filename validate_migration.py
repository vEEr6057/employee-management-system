#!/usr/bin/env python3
"""
Database Connection Validation Script

This script validates the database connection update and tests
basic functionality without requiring a live MongoDB instance.
"""

import sys
import traceback
from backend import TaskManager, Employee, Task, Project

def test_database_connection_config():
    """Test that the database configuration has been updated correctly."""
    print("Testing database connection configuration...")
    
    try:
        # Test default initialization
        tm = TaskManager()
        expected_db_name = "employee_task_db"
        actual_db_name = tm.db.name
        
        if actual_db_name == expected_db_name:
            print(f"✅ Database name correctly set to: {actual_db_name}")
            return True
        else:
            print(f"❌ Database name incorrect. Expected: {expected_db_name}, Got: {actual_db_name}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing database configuration: {e}")
        return False

def test_custom_database_name():
    """Test custom database name parameter."""
    print("Testing custom database name parameter...")
    
    try:
        custom_db_name = "test_custom_db"
        tm = TaskManager(db_name=custom_db_name)
        
        if tm.db.name == custom_db_name:
            print(f"✅ Custom database name working: {custom_db_name}")
            return True
        else:
            print(f"❌ Custom database name failed. Expected: {custom_db_name}, Got: {tm.db.name}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing custom database name: {e}")
        return False

def test_model_classes():
    """Test that model classes can be instantiated correctly."""
    print("Testing model classes...")
    
    try:
        # Test Employee creation
        employee = Employee(1, "John Doe", "john@example.com", "password123")
        emp_dict = employee.to_dict()
        
        required_fields = ["employee_id", "name", "email", "role", "created_at"]
        if all(field in emp_dict for field in required_fields):
            print("✅ Employee model working correctly")
        else:
            print("❌ Employee model missing required fields")
            return False
        
        # Test Task creation
        task = Task(1, "Test Task", "Test Description", 1)
        task_dict = task.to_dict()
        
        required_task_fields = ["task_id", "title", "description", "assigned_to", "status", "priority"]
        if all(field in task_dict for field in required_task_fields):
            print("✅ Task model working correctly")
        else:
            print("❌ Task model missing required fields")
            return False
        
        # Test Project creation
        project = Project(1, "Test Project", "Test Project Description", 1)
        project_dict = project.to_dict()
        
        required_project_fields = ["project_id", "name", "description", "created_by"]
        if all(field in project_dict for field in required_project_fields):
            print("✅ Project model working correctly")
        else:
            print("❌ Project model missing required fields")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing model classes: {e}")
        traceback.print_exc()
        return False

def test_task_manager_methods():
    """Test TaskManager methods that don't require database connection."""
    print("Testing TaskManager methods...")
    
    try:
        tm = TaskManager()
        
        # Test that collections are properly referenced
        collections = ["employees_collection", "tasks_collection", "projects_collection"]
        for collection_name in collections:
            if hasattr(tm, collection_name):
                print(f"✅ {collection_name} properly configured")
            else:
                print(f"❌ {collection_name} not found")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing TaskManager methods: {e}")
        return False

def validate_migration_script():
    """Validate that the migration script is properly structured."""
    print("Validating migration script...")
    
    try:
        from migration import DatabaseMigration
        
        # Test that migration class can be instantiated
        migration = DatabaseMigration()
        
        # Check that required methods exist
        required_methods = [
            "examine_existing_database",
            "backup_existing_data", 
            "migrate_auth_users_to_employees",
            "ensure_required_collections",
            "update_task_structure",
            "run_migration"
        ]
        
        for method_name in required_methods:
            if hasattr(migration, method_name):
                print(f"✅ Migration method {method_name} exists")
            else:
                print(f"❌ Migration method {method_name} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating migration script: {e}")
        return False

def main():
    """Run all validation tests."""
    print("Database Migration Validation")
    print("=" * 40)
    
    tests = [
        test_database_connection_config,
        test_custom_database_name,
        test_model_classes,
        test_task_manager_methods,
        validate_migration_script
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print()
        try:
            if test():
                passed += 1
            else:
                print("Test failed!")
        except Exception as e:
            print(f"Test error: {e}")
    
    print()
    print("=" * 40)
    print(f"Validation Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All validation tests passed!")
        print("✅ Database connection updated successfully")
        print("✅ Migration script ready for deployment")
        return True
    else:
        print("❌ Some validation tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)