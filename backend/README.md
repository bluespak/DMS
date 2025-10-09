# DMS (Digital Message System)
> 🔒 **Digital Will & Message Management System**  
> A comprehensive backend system for managing digital wills, recipients, triggers, and dispatch logs using Flask and MySQL.

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Database Schema](#database-schema)
- [Usage Examples](#usage-examples)
- [Development](#development)
- [Contributing](#contributing)

## 🎯 Overview

DMS is a robust backend system designed to manage digital wills and automated message dispatching. The system allows users to create digital wills, manage recipients, set up triggers for message delivery, and track dispatch logs.

### Key Capabilities
- **Digital Will Management**: Create, update, and manage digital wills
- **Recipient Management**: Maintain recipient lists with contact information
- **Trigger System**: Set up automated triggers for message dispatch (time-based, event-based)
- **Dispatch Logging**: Comprehensive tracking of all message dispatches
- **User Management**: Complete user lifecycle management with authentication
- **RESTful API**: Clean, well-documented REST API endpoints
- **Comprehensive Testing**: Full test coverage with web-based test interface

## 🏗️ Architecture

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│   Flask API     │───▶│   MySQL DB      │
│   (Future)      │    │   (Backend)     │    │   (AWS RDS)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │   Test Suite    │
                       │   (Automated)   │
                       └─────────────────┘
```

### Component Structure
```
DMS/
├── backend/           # Main backend application
│   ├── app/          # Flask application core
│   ├── model/        # Database models (SQLAlchemy)
│   ├── route/        # API route handlers (Blueprint-based)
│   └── tests/        # Comprehensive test suite
├── frontend/         # Frontend application (Future)
└── doc/             # API documentation
```

## ✨ Features

### ✅ Implemented Features
- **User Management API** (UserInfo) - **FULLY TESTED** ✨
  - User registration and authentication
  - Profile management
  - CRUD operations with validation
  - 11/11 test cases passing

### 🏗️ Under Development
- **Will Management API** - Digital will creation and management
- **Recipients API** - Contact and recipient management
- **Triggers API** - Automated trigger configuration
- **Dispatch Log API** - Message dispatch tracking and logging

### 🔧 System Features
- **Modular Architecture**: Clean separation using Flask Blueprints
- **Database Integration**: AWS RDS MySQL with SQLAlchemy ORM
- **Comprehensive Testing**: Automated test suite with web interface
- **API Documentation**: Interactive HTML documentation
- **Error Handling**: Robust error handling and logging
- **Environment Configuration**: Flexible configuration management

## 🛠️ Tech Stack

### Backend Framework
- **Flask 3.1.2** - Python web framework
- **Flask-SQLAlchemy 3.1.1** - ORM and database toolkit
- **Flask-CORS 6.0.1** - Cross-Origin Resource Sharing support
- **PyMySQL 1.1.1** - MySQL database connector

### Database
- **MySQL 8.0.42** - Primary database (AWS RDS)
- **SQLite** - Testing database (in-memory)

### Testing & Development
- **unittest** - Python testing framework
- **Custom Test Runner** - Web-based test execution interface
- **SQLAlchemy Factory Pattern** - Dynamic model creation
- **Blueprint Architecture** - Modular route organization

### Infrastructure
- **AWS RDS** - Managed MySQL database service
- **Environment Variables** - Secure configuration management
- **Logging** - Comprehensive application logging

## 📁 Project Structure

```
DMS/
├── README.md                    # This file
├── backend/
│   ├── .env                     # Environment configuration
│   ├── config.py                # Application configuration
│   ├── requirements.txt         # Python dependencies
│   ├── app/
│   │   └── app.py              # Main Flask application
│   ├── model/                   # Database Models
│   │   ├── userinfo.py         # User model (✅ Complete)
│   │   ├── will.py             # Will model (🏗️ In progress)
│   │   ├── recipients.py       # Recipients model (🏗️ In progress)
│   │   ├── trigger.py          # Trigger model (🏗️ In progress)
│   │   ├── dispatchlog.py      # Dispatch log model (🏗️ In progress)
│   │   ├── createDB.sql        # Database schema
│   │   └── createTables.sql    # Table creation scripts
│   ├── route/                   # API Routes (Blueprint-based)
│   │   ├── userinfo_routes.py  # User management API (✅ Complete)
│   │   ├── will_routes.py      # Will management API (🏗️ In progress)
│   │   ├── recipients_routes.py # Recipients API (🏗️ In progress)
│   │   ├── triggers_routes.py  # Triggers API (🏗️ In progress)
│   │   ├── dispatchlog_routes.py # Dispatch logs API (🏗️ In progress)
│   │   ├── home_routes.py      # Home page routes
│   │   ├── test_routes.py      # Test interface routes
│   │   └── system_routes.py    # System utility routes
│   └── tests/                   # Comprehensive Test Suite
│       ├── simple_test_runner.py # Custom test runner
│       ├── test_config.py      # Test configuration
│       ├── test_userinfo_api.py # UserInfo API tests (✅ 11/11 passing)
│       ├── test_will_api.py    # Will API tests (🏗️ In progress)
│       ├── test_recipients_api.py # Recipients API tests (🏗️ In progress)
│       ├── test_triggers_api.py # Triggers API tests (🏗️ In progress)
│       └── test_dispatchlog_api.py # Dispatch log API tests (🏗️ In progress)
├── frontend/                    # Frontend Application (Future)
└── doc/
    └── api-documentation.html   # Interactive API documentation
```

## 🚀 Installation

### Prerequisites
- Python 3.13+
- MySQL 8.0+ (or AWS RDS MySQL instance)
- Virtual environment (recommended)

### Step 1: Clone Repository
```bash
git clone https://github.com/bluespak/DMS.git
cd DMS
```

### Step 2: Create Virtual Environment
```bash
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Environment Configuration
Create `.env` file in the backend directory:
```env
# Database Configuration
DB_HOST=your-database-host
DB_PORT=3306
DB_USER=your-username
DB_PASSWORD=your-password
DB_NAME=your-database-name

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key
```

### Step 5: Database Setup
```bash
# Run database creation scripts
mysql -h your-host -u your-user -p your-database < model/createDB.sql
mysql -h your-host -u your-user -p your-database < model/createTables.sql
```

### Step 6: Run Application
```bash
cd app
python app.py
```

The application will be available at: `http://127.0.0.1:5000`

## ⚙️ Configuration

### Database Configuration (`config.py`)
```python
class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@host/database'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
```

### Test Configuration (`tests/test_config.py`)
```python
class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

## 📚 API Documentation

### Base URL
```
http://127.0.0.1:5000/api
```

### UserInfo API (✅ Fully Implemented)

#### Endpoints Overview
| Method | Endpoint | Description | Status |
|--------|----------|-------------|---------|
| GET | `/api/userinfo` | Get all users | ✅ Working |
| POST | `/api/userinfo` | Create new user | ✅ Working |
| GET | `/api/userinfo/{id}` | Get user by ID | ✅ Working |
| PUT | `/api/userinfo/{id}` | Update user | ✅ Working |
| DELETE | `/api/userinfo/{id}` | Delete user | ✅ Working |

#### Request/Response Examples

**Create User:**
```http
POST /api/userinfo
Content-Type: application/json

{
    "name": "John Doe",
    "birth_date": "1990-01-15",
    "email": "john.doe@example.com",
    "phone": "010-1234-5678"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "John Doe",
        "birth_date": "1990-01-15",
        "email": "john.doe@example.com",
        "phone": "010-1234-5678",
        "created_at": "2025-10-09T10:30:00",
        "updated_at": "2025-10-09T10:30:00"
    }
}
```

### Future APIs (🏗️ In Development)
- **Will API**: `/api/wills` - Digital will management
- **Recipients API**: `/api/recipients` - Recipient management
- **Triggers API**: `/api/triggers` - Trigger configuration
- **Dispatch Log API**: `/api/dispatch-logs` - Message dispatch tracking

### Interactive Documentation
Visit: `http://127.0.0.1:5000/api/docs` for interactive API documentation.

## 🧪 Testing

### Test Suite Overview
- **Total Test Cases**: 52 tests across all APIs
- **UserInfo API**: 11/11 tests passing ✅
- **Other APIs**: 41 tests (under development) 🏗️

### Running Tests

#### Web-based Test Interface (Recommended)
1. Start the Flask application:
   ```bash
   cd backend/app
   python app.py
   ```

2. Navigate to test interface:
   ```
   http://127.0.0.1:5000/test
   ```

3. Click "UserInfo 테스트만" for current working tests

#### Command Line Testing
```bash
cd backend/tests
python simple_test_runner.py
```

### Test Configuration
- **Testing Database**: SQLite in-memory (isolated from production)
- **Test Data**: Automatically generated and cleaned up
- **Assertions**: Comprehensive validation of responses and database state

### UserInfo API Test Coverage
```
✅ test_create_user_success - User creation with valid data
✅ test_create_user_no_data - Validation for missing data
✅ test_create_user_invalid_date - Date format validation
✅ test_get_all_users_empty - Empty database handling
✅ test_get_all_users_with_data - Multiple users retrieval
✅ test_get_user_by_id_success - Individual user retrieval
✅ test_get_user_by_id_not_found - 404 error handling
✅ test_update_user_success - User information updates
✅ test_update_user_not_found - Update non-existent user
✅ test_delete_user_success - User deletion
✅ test_delete_user_not_found - Delete non-existent user
```

## 🗄️ Database Schema

### UserInfo Table (✅ Implemented)
```sql
CREATE TABLE userinfo (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Future Tables (🏗️ Schema Ready)
- **will**: Digital will storage and metadata
- **recipients**: Contact information and relationships
- **trigger**: Automated trigger configurations
- **dispatch_log**: Message dispatch tracking

### Database Relationships
```
UserInfo (1) ────── (N) Will
Will (1) ─────────── (N) Recipients  
UserInfo (1) ────── (N) Trigger
Will (1) ─────────── (N) DispatchLog
Recipients (1) ──── (N) DispatchLog
```

## 💡 Usage Examples

### Starting the Application
```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # Linux/Mac

# Start Flask application
cd backend/app
python app.py
```

### Creating a User via API
```python
import requests

url = "http://127.0.0.1:5000/api/userinfo"
data = {
    "name": "Alice Smith",
    "birth_date": "1985-03-20",
    "email": "alice.smith@example.com",
    "phone": "010-9876-5432"
}

response = requests.post(url, json=data)
print(response.json())
```

### Running Tests
```bash
# Web interface
# Navigate to: http://127.0.0.1:5000/test

# Command line
cd backend/tests
python simple_test_runner.py
```

## 🔧 Development

### Development Workflow
1. **Model Development**: Create SQLAlchemy models in `model/`
2. **Route Development**: Implement Flask Blueprints in `route/`
3. **Test Development**: Write comprehensive tests in `tests/`
4. **Integration**: Register blueprints in `app/app.py`
5. **Testing**: Validate via web interface or command line

### Code Organization Principles
- **Factory Pattern**: Models and routes use factory functions for dependency injection
- **Blueprint Architecture**: Modular route organization
- **Separation of Concerns**: Clear separation between models, routes, and business logic
- **Comprehensive Testing**: Every endpoint has corresponding test cases

### Adding New APIs
1. Create model in `model/new_model.py`
2. Create routes in `route/new_routes.py`
3. Create tests in `tests/test_new_api.py`
4. Register blueprint in `app/app.py`
5. Update test runner to include new tests

## 📊 Current Status

### ✅ Production Ready
- **UserInfo API**: Complete CRUD operations with full test coverage
- **Database Integration**: AWS RDS MySQL connection established
- **Test Infrastructure**: Web-based testing interface operational
- **Documentation**: Comprehensive API documentation available

### 🏗️ In Development
- **Will Management API**: Routes implemented, tests need debugging
- **Recipients API**: Routes implemented, tests need debugging  
- **Triggers API**: Routes implemented, tests need debugging
- **Dispatch Log API**: Routes implemented, tests need debugging

### 🎯 Next Steps
1. **Debug API Tests**: Resolve 404 errors in non-UserInfo APIs
2. **Complete API Implementation**: Ensure all APIs work like UserInfo
3. **Frontend Development**: Create React/Vue.js interface
4. **Authentication**: Implement JWT-based authentication
5. **Deployment**: Configure production deployment

## 🤝 Contributing

### Getting Started
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `python backend/tests/simple_test_runner.py`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for API changes
- Use descriptive commit messages
- Ensure all tests pass before submitting PR

### Testing Requirements
- All new APIs must have corresponding test cases
- Test coverage should be maintained at 100% for implemented features
- Use the web-based test interface for validation

---

## 📞 Contact & Support

- **Repository**: [https://github.com/bluespak/DMS](https://github.com/bluespak/DMS)
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Documentation**: Full API docs available at `/api/docs` when running

---

**Last Updated**: October 9, 2025  
**Version**: 1.0.0 (UserInfo API Complete)  
**Status**: Active Development 🚧
