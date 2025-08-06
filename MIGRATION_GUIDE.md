# Database Migration Guide

## Overview

This guide explains the database migration process for the Employee Management System to connect to the existing `employee_task_db` database instead of the default `employee_management` database.

## Changes Made

### 1. Database Connection Update

**File:** `backend.py`
- **Line 98:** Changed default database name from `employee_management` to `employee_task_db`
- **Before:** `db_name: str = "employee_management"`
- **After:** `db_name: str = "employee_task_db"`

### 2. Migration Script

**File:** `migration.py`
- Comprehensive migration script that handles data preservation and schema updates
- Includes backup functionality to protect existing data
- Maps `auth_users` collection to `employees` collection structure
- Ensures all required collections exist (`employees`, `tasks`, `projects`)
- Updates task structure to match backend expectations

### 3. Validation Script

**File:** `validate_migration.py`
- Validates database configuration changes
- Tests model classes and TaskManager functionality
- Confirms migration script is properly structured

## Migration Process

### Step 1: Pre-Migration Validation

Run the validation script to ensure everything is configured correctly:

```bash
python3 validate_migration.py
```

### Step 2: Run Migration (When MongoDB is Available)

Execute the migration script to preserve existing data:

```bash
python3 migration.py
```

The migration script will:
1. **Examine** existing database structure
2. **Backup** all existing data to `employee_task_db_backup`
3. **Migrate** auth_users to employees collection
4. **Ensure** required collections exist
5. **Update** task structure to match backend requirements

### Step 3: Start the Application

Start the FastAPI backend:

```bash
python3 fastapi_app.py
```

Or using uvicorn:

```bash
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
```

## Data Mapping

### auth_users → employees

| auth_users field | employees field | Notes |
|------------------|-----------------|-------|
| user_id/id | employee_id | Primary identifier |
| name/username | name | Employee display name |
| email | email | Unique identifier |
| role | role | User role (Employee/Manager) |
| password_hash | password_hash | Hashed password |
| created_at | created_at | Account creation timestamp |

### Existing Collections Preserved

- **employees**: User account information
- **tasks**: Task management data with time logs
- **projects**: Project information (created if missing)

## Database Schema

### employees Collection
```json
{
  "employee_id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "Employee",
  "password_hash": "bcrypt_hash",
  "created_at": "2024-01-01T00:00:00"
}
```

### tasks Collection
```json
{
  "task_id": 1,
  "title": "Task Title",
  "description": "Task Description",
  "assigned_to": 1,
  "priority": "Medium",
  "status": "Pending",
  "project_id": 1,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "time_logs": [
    {
      "employee_id": 1,
      "hours": 2.5,
      "description": "Work description",
      "logged_at": "2024-01-01T00:00:00"
    }
  ]
}
```

### projects Collection
```json
{
  "project_id": 1,
  "name": "Project Name",
  "description": "Project Description",
  "created_by": 1,
  "created_at": "2024-01-01T00:00:00"
}
```

## API Endpoints

All existing API endpoints continue to work with the migrated database:

- **Authentication:** `/auth/register`, `/auth/login`
- **Employees:** `/employees`, `/employees/me`, `/employees/{id}`
- **Tasks:** `/tasks`, `/tasks/{id}`, `/tasks/{id}/status`
- **Time Tracking:** `/tasks/{id}/time-log`, `/employees/{id}/time-logs`
- **Projects:** `/projects`, `/projects/{id}`, `/projects/{id}/tasks`
- **Dashboard:** `/dashboard/stats`

## Backup and Recovery

### Automatic Backup
The migration script automatically creates a backup in `employee_task_db_backup` database before making any changes.

### Manual Backup
To manually backup the database:

```bash
mongodump --db employee_task_db --out backup_$(date +%Y%m%d_%H%M%S)
```

### Restore from Backup
To restore from the automatic backup:

```javascript
// In MongoDB shell
use employee_task_db_backup
db.copyDatabase("employee_task_db_backup", "employee_task_db")
```

## Troubleshooting

### Connection Issues
- Ensure MongoDB is running on `localhost:27017`
- Check MongoDB service status: `sudo systemctl status mongod`
- Verify database name in connection string

### Migration Issues
- Check MongoDB logs for errors
- Verify backup was created successfully
- Review migration script output for specific errors

### Authentication Issues
- Verify user passwords are properly hashed
- Check JWT secret key configuration
- Ensure email addresses are unique

## Testing the Migration

### 1. Database Connection Test
```python
python3 -c "from backend import TaskManager; tm = TaskManager(); print('Connected to:', tm.db.name)"
```

### 2. API Test
```bash
curl http://localhost:8000/
```

### 3. Frontend Test
Start the Next.js frontend and verify it can connect to the API:
```bash
npm run dev
```

## Security Considerations

- All passwords are bcrypt hashed
- JWT tokens have 24-hour expiration
- Backup database contains sensitive data - secure appropriately
- Default password for migrated users without passwords is "changeme" - users should update immediately

## Support

If issues arise during migration:
1. Check the backup was created successfully
2. Review migration script logs
3. Test database connectivity
4. Verify API endpoints respond correctly
5. Check frontend can authenticate and load data