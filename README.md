# Choose Your Own Adventure

A dual-service web application that delivers an interactive **Choose Your Own Adventure** storytelling experience.

This project follows a **microservices architecture**, separating the user interface from the story engine:

- **Django Frontend** → Handles UI, authentication, and story rendering  
- **Flask API Backend** → Handles story logic, nodes, and transitions

---

## Architecture Overview

- **Django** manages:
  - User accounts
  - Session state
  - Story presentation

- **Flask** acts as:
  - The game engine
  - Story logic handler
  - Story content provider

---

## Project Structure

```
Choose_Your_Own_Adventure/
│
├── docker-compose.yml # Runs both services together
├── README.md
│
├── django-app/ # FRONTEND (Django)
│ ├── Dockerfile
│ ├── manage.py
│ ├── requirements.txt
│ ├── db.sqlite3 # User database (ignored in Git)
│ │
│ ├── nahb/ # Project configuration
│ │ ├── settings.py
│ │ ├── urls.py
│ │ └── wsgi.py
│ │
│ ├── stories/ # Application logic
│ │ ├── models.py
│ │ ├── views.py
│ │ └── urls.py
│ │
│ └── templates/
│ ├── registration/
│ └── stories/
│
└── flask-api/ # BACKEND (Flask)
├── Dockerfile
├── run.py
├── requirements.txt
│
├── app/
│ ├── init.py
│ ├── models.py
│ └── routes.py
│
└── instance/
└── flask-db.sqlite # Story database
```

---

## Prerequisites

### Recommended (Docker Method)

- Docker  
- Docker Compose  

### Manual Setup

- Python **3.12+**
- Git

---

# Running the Application

---

## Method 1: Docker (Recommended)

This method ensures consistent dependencies and networking.

### 1. Start Services

From the project root:

```bash
docker-compose up --build

2. Access the Application

Frontend (Django):
http://localhost:8000

Backend API (Flask):
http://localhost:5000
```

3. Stop Services
docker-compose down

Method 2: Manual Installation

Run Django and Flask in separate terminals.

Part A: Start Flask API
cd flask-api
python -m venv venv


Activate the environment:

Windows

.\venv\Scripts\activate


Mac/Linux

source venv/bin/activate


Install dependencies:

pip install -r requirements.txt


Run Flask:

python run.py


Flask runs at:

http://127.0.0.1:5000

Part B: Start Django App
cd django-app
python -m venv venv


Activate environment (same as above).

Install dependencies:

pip install -r requirements.txt

Configure API Connection

Since Docker networking is not used:

Windows (PowerShell)

$env:FLASK_API_URL = "http://127.0.0.1:5000"


Windows (CMD)

set FLASK_API_URL=http://127.0.0.1:5000


Mac/Linux

export FLASK_API_URL=http://127.0.0.1:5000

Run Django
python manage.py migrate
python manage.py runserver


Django runs at:

http://127.0.0.1:8000

How It Works
Django Frontend

Displays story text and choices

Manages authentication

Sends user decisions to Flask API

Flask API

Receives story node requests

Determines next node

Returns story data as JSON

Example Flow:

User Choice → Django View → Flask API → JSON Response → Rendered Page

Data Storage
Service	Responsibility
Django	Users & Progress
Flask	Story Content & Logic
