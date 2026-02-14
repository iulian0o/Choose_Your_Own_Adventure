# Choose Your Own Adventure

A dual-service web application that delivers an interactive Choose Your Own Adventure storytelling experience.

This project follows a microservices architecture, separating the user interface from the story engine:

- **Django Frontend** → Handles UI, authentication, and story rendering
- **Flask API Backend** → Handles story logic, nodes, and transitions

## Architecture Overview

### Django manages:
- User accounts
- Session state
- Story presentation
- User ratings and statistics

### Flask acts as:
- The game engine
- Story logic handler
- Story content provider

## Project Structure

```
Choose_Your_Own_Adventure/
│
├── docker-compose.yml          # Runs both services together
├── README.md
│
├── django-app/                 # FRONTEND (Django)
│   ├── Dockerfile
│   ├── manage.py
│   ├── requirements.txt
│   ├── db.sqlite3             # User database (ignored in Git)
│   │
│   ├── nahb/                  # Project configuration
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── stories/               # Application logic
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── forms.py
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── registration/
│   │   ├── stories/
│   │   ├── play/
│   │   └── author/
│   │
│   └── static/
│       ├── css/
│       │   └── tailus-minimal.css
│       └── scss/
│           └── tailus-minimal.scss
│
└── flask-api/                 # BACKEND (Flask)
    ├── Dockerfile
    ├── run.py
    ├── requirements.txt
    │
    ├── app/
    │   ├── __init__.py
    │   ├── models.py
    │   └── routes.py
    │
    └── instance/
        └── stories.db         # Story database
```

## Prerequisites

### Recommended (Docker Method)
- Docker
- Docker Compose

### Manual Setup
- Python 3.8+
- Git

## Running the Application

### Method 1: Docker (Recommended)

This method ensures consistent dependencies and networking.

#### 1. Start Services

From the project root:

```bash
docker-compose up --build
```

#### 2. Access the Application

- **Frontend (Django):** `http://localhost:8000`
- **Backend API (Flask):** `http://localhost:5000`

#### 3. Stop Services

```bash
docker-compose down
```

---

### Method 2: Manual Installation

Run Django and Flask in separate terminals.

#### Part A: Start Flask API

```bash
cd flask-api
python -m venv venv
```

**Activate the environment:**

Windows (PowerShell):
```powershell
.\venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run Flask:**
```bash
python run.py
```

Flask runs at: `http://127.0.0.1:5000`

---

#### Part B: Start Django App

```bash
cd django-app
python -m venv venv
```

**Activate environment** (same as above)

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Configure API Connection**

Since Docker networking is not used, set the Flask API URL:

Windows (PowerShell):
```powershell
$env:FLASK_API_URL = "http://127.0.0.1:5000"
```

Windows (CMD):
```cmd
set FLASK_API_URL=http://127.0.0.1:5000
```

Mac/Linux:
```bash
export FLASK_API_URL=http://127.0.0.1:5000
```

**Run migrations and start Django:**
```bash
python manage.py migrate
python manage.py createsuperuser  # Create admin account
python manage.py runserver
```

Django runs at: `http://127.0.0.1:8000`

## How It Works

### Django Frontend
- Displays story text and choices
- Manages authentication
- Sends user decisions to Flask API
- Tracks user ratings and statistics

### Flask API
- Receives story node requests
- Determines next node based on choices
- Returns story data as JSON

### Example Flow:
```text
User Choice → Django View → Flask API → JSON Response → Rendered Page
```

## Features

### User Features
- **User Registration & Login** - Create account to access stories
- **Story Browsing** - View all available stories with ratings
- **Interactive Gameplay** - Make choices that affect the story outcome
- **Multiple Endings** - Each story has multiple possible endings
- **Rating System** - Rate stories with 1-5 stars and leave comments
- **Statistics** - View play counts and ending distributions

### Author Features
- **Story Creation** - Create stories with branching paths
- **Simple Editor** - Easy-to-use form for creating 2-page stories with 2 endings
- **Story Management** - Edit titles/descriptions or delete stories
- **Preview** - Test stories before others see them

## API Documentation

### Flask REST API Endpoints

#### Reading (Public)
```http
GET  /stories                    # List all published stories
GET  /stories/<id>               # Get specific story details
GET  /stories/<id>/start         # Get story starting page
GET  /pages/<id>                 # Get page with choices
```

#### Writing (Author Only)
```http
POST   /stories                  # Create new story
PUT    /stories/<id>             # Update story
DELETE /stories/<id>             # Delete story
POST   /stories/<id>/pages       # Add page to story
POST   /pages/<id>/choices       # Add choice to page
PUT    /pages/<id>               # Update page
DELETE /pages/<id>               # Delete page
DELETE /choices/<id>             # Delete choice
```

## Database Schema

### Flask Database (stories.db)
- **Story** - Story metadata (title, description, status)
- **Page** - Story pages and endings
- **Choice** - Choices that link pages together

### Django Database (db.sqlite3)
- **User** - Django authentication
- **Play** - Gameplay statistics
- **PlaySession** - Active gameplay sessions
- **Rating** - User ratings and comments

## Technology Stack

- **Backend:** Flask 3.0+, SQLAlchemy, Flask-CORS
- **Frontend:** Django 5.0+, Django Templates
- **Database:** SQLite (both services)
- **Styling:** Custom SCSS compiled to CSS
- **Authentication:** Django Auth System

## Development

### Adding Sample Stories

```powershell
cd flask-api
.\venv\Scripts\activate
python create_branching_stories.py
```

This creates 3 sample stories with multiple endings.

### Running Tests

```bash
# Django tests
cd django-app
python manage.py test

# Flask tests
cd flask-api
pytest
```

## Troubleshooting

### Flask won't start
```powershell
# Ensure virtual environment is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Django migrations fail
```powershell
# Delete database and migrations
del db.sqlite3
del stories\migrations\0*.py

# Recreate
python manage.py makemigrations stories
python manage.py migrate
python manage.py createsuperuser
```

### Stories don't appear
- Verify Flask is running on port 5000
- Check Flask API directly: `http://localhost:5000/stories`
- Ensure story status is "published"
- Check Django terminal for connection errors

## Contributing

This is a student project for educational purposes. Contributions and suggestions are welcome!

## License

This project is created for educational purposes as part of a university course requirement.

## The UI is inspired by this:

```
https://github.com/Tailus-UI/astro-theme 
```


