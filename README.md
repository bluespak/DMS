# Dead Man's Switch (DMS)

A web application that ensures important messages are delivered if you fail to check in regularly. Perfect for emergency communications, password recovery, or final messages to loved ones.

## Features

- **User Authentication**: Secure registration and login
- **Switch Management**: Create and manage multiple dead man's switches
- **Flexible Check-in Intervals**: Set custom check-in periods (in days)
- **Multiple Recipients**: Send different messages to multiple recipients
- **Automatic Triggering**: Messages are sent automatically if check-in is missed
- **Dashboard**: Monitor all your switches and their status
- **Check-in Reminders**: See days remaining until trigger

## Technology Stack

### Backend
- **Python 3.12+**
- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Database (easily replaceable with PostgreSQL/MySQL)
- **APScheduler**: Background task scheduler
- **JWT Authentication**: Secure token-based auth

### Frontend
- **React.js**: UI library
- **React Router**: Navigation
- **Axios**: HTTP client
- **Vite**: Build tool

## Installation

### Prerequisites
- Python 3.12 or higher
- Node.js 20 or higher
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

5. Edit `.env` with your configuration:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./dms.db
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@deadmanswitch.com
```

6. Run the backend:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

### Creating a Switch

1. Register or login to your account
2. Click "Create New Switch" on the dashboard
3. Set a name for your switch (e.g., "Emergency Contact")
4. Choose a check-in interval (e.g., 7 days)
5. Add one or more messages with:
   - Recipient email
   - Subject line
   - Message body
6. Click "Create Switch"

### Checking In

1. Go to your dashboard
2. Find the switch you want to check in to
3. Click "Check In" button
4. Your check-in timer resets

### What Happens If You Don't Check In?

If you fail to check in before the deadline:
1. The switch is automatically triggered
2. All configured messages are sent to recipients
3. The switch is marked as "Triggered"
4. No further check-ins are possible for that switch

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

### Main Endpoints

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user
- `GET /api/switches` - List all switches
- `POST /api/switches` - Create new switch
- `GET /api/switches/{id}` - Get switch details
- `PATCH /api/switches/{id}` - Update switch
- `DELETE /api/switches/{id}` - Delete switch
- `POST /api/switches/{id}/checkin` - Check in to switch

## Email Configuration

To enable email sending, configure SMTP settings in `.env`:

### Using Gmail
1. Enable 2-factor authentication
2. Create an app password
3. Use the app password in `SMTP_PASSWORD`

### Using Other Providers
Update `SMTP_HOST` and `SMTP_PORT` accordingly.

## Development

### Backend Testing
```bash
cd backend
pytest  # If tests are added
```

### Frontend Testing
```bash
cd frontend
npm test  # If tests are added
```

### Building for Production

Backend:
```bash
# Use gunicorn or similar ASGI server
gunicorn main:app --worker-class uvicorn.workers.UvicornWorker
```

Frontend:
```bash
cd frontend
npm run build
# Serve the dist/ folder with a static server
```

## Security Considerations

- Change `SECRET_KEY` in production
- Use HTTPS in production
- Use a proper database (PostgreSQL, MySQL) in production
- Store sensitive credentials in environment variables
- Implement rate limiting for API endpoints
- Add email verification for new accounts
- Implement two-factor authentication

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
