# DMS (Dead Man's Switch)
> ⚡ **Digital Memory Service - Automated Message Dispatch System**  
> A comprehensive full-stack system for managing digital wills, automated triggers, and secure message delivery using React + Flask + MySQL.

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Frontend Guide](#frontend-guide)
- [Testing](#testing)
- [Database Schema](#database-schema)
- [Usage Examples](#usage-examples)
- [Development](#development)
- [Contributing](#contributing)

## 🎯 Overview

DMS (Dead Man's Switch) is a full-stack digital legacy management system that automatically sends pre-written messages to designated recipients when a user becomes inactive for a specified period. Think of it as a "digital failsafe" for important communications.

### Key Capabilities
- **🏠 User-Friendly Interface**: React-based responsive web application
- **🔐 Secure Authentication**: JWT-based login system with session management
- **📜 Digital Will Management**: Create, edit, and manage digital wills with rich content
- **📧 Smart Recipients**: Manage recipient lists with email validation
- **⚡ Intelligent Triggers**: Automated inactivity detection with customizable timeouts
- **📨 Dispatch Tracking**: Comprehensive logging of all message deliveries
- **👥 User Management**: Complete user lifecycle with admin panel
- **🛡️ Security First**: Encrypted data, secure API endpoints, comprehensive logging
- **🧪 Full Test Coverage**: Automated testing with API documentation

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

### Frontend
- **React 18.2.0** - Modern JavaScript library for building user interfaces
- **Create React App 5.0.1** - Zero-configuration React development environment
- **Node.js 18+** - JavaScript runtime for development tools
- **npm/yarn** - Package management and build tools
- **Axios 1.6.0** - HTTP client for API communication
- **CSS3** - Modern styling with responsive design
- **React Hooks** - Functional component state management
- **Development Proxy** - Automatic API proxying to Flask backend (port 5000)

### Backend Framework
- **Flask 3.1.2** - Python web framework
- **Flask-SQLAlchemy 3.1.1** - ORM and database toolkit
- **Flask-CORS 6.0.1** - Cross-Origin Resource Sharing support
- **PyMySQL 1.1.1** - MySQL database connector
- **cryptography** - Database authentication encryption

### Authentication & Security
- **JWT (JSON Web Tokens)** - Stateless authentication
- **Flask-JWT-Extended** - JWT integration for Flask
- **Password Hashing** - Secure password storage
- **CORS Configuration** - Cross-origin request handling

### Database
- **MySQL 8.0.42** - Primary database (AWS RDS)
- **SQLite** - Testing database (in-memory)
- **SQLAlchemy ORM** - Object-relational mapping

### Testing & Development
- **unittest** - Python testing framework
- **Custom Test Runner** - Web-based test execution interface
- **SQLAlchemy Factory Pattern** - Dynamic model creation
- **Blueprint Architecture** - Modular route organization
- **ESLint** - JavaScript code quality analysis

### Infrastructure & DevOps
- **AWS RDS** - Managed MySQL database service  
- **Environment Variables** - Secure configuration management
- **Comprehensive Logging** - Application and error logging
- **Development Proxy** - React dev server to Flask backend

## 📁 Project Structure

```
DMS/
├── README.md                    # Project documentation
├── doc/                         # Documentation files
│   ├── API_Documentation_v2.md  # Comprehensive API documentation
│   ├── api-documentation.html   # Interactive API documentation
│   └── API_Testing_Guide.md     # Testing guidelines
├── frontend/                    # React Frontend Application
│   ├── package.json            # Node.js dependencies
│   ├── public/
│   │   └── index.html          # Main HTML template
│   ├── src/
│   │   ├── App.js              # Main React component
│   │   ├── App.css             # Global styles
│   │   ├── index.js            # React entry point
│   │   ├── components/         # React components
│   │   │   ├── DeadManSwitchHome.js # Main dashboard
│   │   │   ├── HomePage.js     # Home page component
│   │   │   ├── RegisterPage.js # User registration
│   │   │   ├── WillEditor.js   # Will creation/editing
│   │   │   └── UserProfilePage.js # User profile management
│   │   ├── config/             # Frontend configuration
│   │   ├── services/           # API service layer
│   │   └── utils/              # Utility functions
│   └── logs/                   # Frontend logging
└── backend/                    # Flask Backend API
    ├── .env                    # Environment configuration
    ├── config.py               # Application configuration
    ├── requirements.txt        # Python dependencies
    ├── app/
    │   └── app.py             # Main Flask application
    ├── models/                 # Database Models (SQLAlchemy)
    │   ├── userinfo.py        # User model (✅ Complete)
    │   ├── will.py            # Will model (✅ Complete)
    │   ├── recipients.py      # Recipients model (✅ Complete)
    │   ├── trigger.py         # Trigger model (✅ Complete) 
    │   ├── dispatchlog.py     # Dispatch log model (✅ Complete)
    │   ├── createDB.sql       # Database schema
    │   └── createTables.sql   # Table creation scripts
    ├── routes/                 # API Routes (Blueprint Architecture)
    │   ├── auth_routes.py     # Authentication API (✅ Complete)
    │   ├── userinfo_routes.py # User management API (✅ Complete)
    │   ├── will_routes.py     # Will management API (✅ Complete)
    │   ├── recipients_routes.py # Recipients API (✅ Complete)
    │   ├── triggers_routes.py # Triggers API (✅ Complete)
    │   ├── dispatchlog_routes.py # Dispatch logs API (✅ Complete)
    │   ├── home_routes.py     # Home page routes (✅ Complete)
    │   ├── test_routes.py     # Test interface routes (✅ Complete)
    │   └── system_routes.py   # System utility routes (✅ Complete)
    ├── tests/                  # Comprehensive Test Suite
    │   ├── simple_test_runner.py # Custom test runner
    │   ├── test_config.py     # Test configuration
    │   ├── test_auth_api.py   # Authentication API tests (✅ Complete)
    │   ├── test_userinfo_api.py # User API tests (✅ Updated)
    │   ├── test_will_api.py   # Will API tests (🔄 Needs update)
    │   ├── test_recipients_api.py # Recipients API tests (🔄 Needs update)
    │   ├── test_triggers_api.py # Triggers API tests (🔄 Needs update)
    │   └── test_dispatchlog_api.py # Dispatch logs API tests (🔄 Needs update)
    ├── utils/                  # Utility modules
    │   ├── log_manager.py     # Logging management
    │   └── logging_config.py  # Logging configuration
    └── logs/                   # Application logging
        ├── data/              # Data operation logs
        ├── server/            # Server logs
        └── system/            # System logs
```

## 🚀 Installation

### Prerequisites
- **Python 3.13+** - Backend development
- **Node.js 18+** - Frontend development
- **npm 9+** or **yarn 1.22+** - Package manager
- **MySQL 8.0+** (or AWS RDS MySQL instance) - Database
- **Virtual environment** (recommended for Python)

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

### Step 3: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Install Frontend Dependencies
```bash
cd ../frontend
npm install
# or with yarn
yarn install
```

### Step 5: Environment Configuration

#### Backend Configuration
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

#### Frontend Configuration
The frontend is pre-configured with a proxy to the Flask backend (`http://localhost:5000`).
No additional configuration needed for development.

### Step 6: Database Setup
```bash
# Run database creation scripts
mysql -h your-host -u your-user -p your-database < model/createDB.sql
mysql -h your-host -u your-user -p your-database < model/createTables.sql
```

### Step 7: Run Applications

#### Start Backend Server
```bash
cd backend/app
python app.py
```
Backend API will be available at: `http://127.0.0.1:5000`

#### Start Frontend Development Server
```bash
cd frontend
npm start
# or with yarn
yarn start
```
React application will be available at: `http://localhost:3000`

The frontend automatically proxies API requests to the backend server.

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

### Starting the Full-Stack Application

#### Backend (Flask API)
```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # Linux/Mac

# Start Flask application
cd backend/app
python app.py
```
API available at: `http://127.0.0.1:5000`

#### Frontend (React App)
```bash
# In a new terminal
cd frontend
npm start
```
Web application available at: `http://localhost:3000`

**Note**: Start the backend first, then the frontend. The React app will automatically proxy API calls to the Flask backend.

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
4. Run backend tests: `python backend/tests/simple_test_runner.py`
5. Test frontend: `cd frontend && npm test`
6. Commit changes: `git commit -m 'Add amazing feature'`
7. Push to branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

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
