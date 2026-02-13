Choose Your Own Adventure
This project is a dual-service web application that creates an interactive "Choose Your Own Adventure" story platform. It consists of a Django frontend that manages user interaction and a Flask API backend that serves story logic and data.

Project Structure
django-app/: The frontend web application (Django). Contains the UI, user authentication, and story rendering logic.

flask-api/: The backend API (Flask). Manages the story nodes, logic, and database state.

Prerequisites
Docker & Docker Compose (Recommended for Method 1)

Python 3.12+ (Required for Method 2)

Git

Method 1: Run with Docker (Recommended)
This is the simplest method. It ensures both services run in an isolated environment with the correct networking and dependencies configured automatically.

Open a terminal in the project root directory (where docker-compose.yml is located).

Build and start the services:

Bash
docker-compose up --build
Wait for the logs. You should see success messages indicating both the Flask API and Django development server have started.

Access the application:

Frontend (Django): http://localhost:8000

Backend API (Flask): http://localhost:5000

Stop the application:
Press Ctrl + C in the terminal, or run:

Bash
docker-compose down
Method 2: Manual Installation (Local)
If you cannot use Docker, you must run the Flask API and the Django app in two separate terminals.

Part A: Start the Flask API
Open a new terminal and navigate to the flask directory:

Bash
cd flask-api
Create a virtual environment:

Bash
python -m venv venv
Activate the virtual environment:

Windows: .\venv\Scripts\activate

Mac/Linux: source venv/bin/activate

Install dependencies:

Bash
pip install -r requirements.txt
Run the Flask application:

Bash
python run.py
The API will start at http://127.0.0.1:5000

Part B: Start the Django App
Open a second terminal and navigate to the django directory:

Bash
cd django-app
Create a virtual environment:

Bash
python -m venv venv
Activate the virtual environment:

Windows: .\venv\Scripts\activate

Mac/Linux: source venv/bin/activate

Install dependencies:

Bash
pip install -r requirements.txt
Important: Configure the API connection.
Since you are running locally (not in Docker), Django needs to know Flask is at localhost, not flask-api. Set the environment variable before running the server.

Windows (PowerShell):

PowerShell
$env:FLASK_API_URL = "http://127.0.0.1:5000"
Windows (CMD):

DOS
set FLASK_API_URL=http://127.0.0.1:5000
Mac/Linux:

Bash
export FLASK_API_URL=http://127.0.0.1:5000
Run database migrations:

Bash
python manage.py migrate
Start the Django server:

Bash
python manage.py runserver
Access the application at http://127.0.0.1:8000.

Troubleshooting
Docker Issues
If the build fails with "No matching distribution found for Django," ensure your Dockerfile is using FROM python:3.12-slim.

If you see "connection refused" errors between Django and Flask, ensure you are not using localhost inside the docker-compose.yml. The Django environment variable must be set to FLASK_API_URL=http://flask-api:5000.

Manual Run Issues
If Django cannot connect to Flask, ensure the Flask terminal is still running and that you set the $env:FLASK_API_URL correctly in the Django terminal before starting the server.

How It Works
This application uses a microservices architecture to separate the user interface from the game logic:

The Frontend (Django):

Handles all user interactions, displaying the story text and choices.

Manages user authentication (login/signup) and session state.

When a user makes a choice, Django sends an HTTP request to the Flask API.

The Backend API (Flask):

Acts as the game engine.

Receives the current story node ID from Django.

Retrieves the next part of the story and available choices from its internal database.

Returns this data as JSON back to Django.

Data Storage:

Django: Stores user accounts and progress.

Flask: Stores the static story content (nodes, text, and transitions).

Project Structure
This directory tree highlights the key files and their purposes based on your current setup.

Plaintext
Choose_Your_Own_Adventure/
├── docker-compose.yml       # Defines how to run both apps together
├── README.md                # Project documentation
│
├── django-app/              # FRONTEND: User Interface & Auth
│   ├── Dockerfile           # Instructions to build the Django image
│   ├── manage.py            # Django command-line utility
│   ├── requirements.txt     # Python dependencies for Django
│   ├── db.sqlite3           # User database (ignorable in git)
│   │
│   ├── nahb/                # Main Project Settings
│   │   ├── settings.py      # Config (Apps, Middleware, Database)
│   │   ├── urls.py          # Main URL routing
│   │   └── wsgi.py          # Entry point for web servers
│   │
│   ├── stories/             # App Logic
│   │   ├── models.py        # Database models for user progress
│   │   ├── views.py         # Handles requests and talks to Flask API
│   │   └── urls.py          # URL routing for story pages
│   │
│   └── templates/           # HTML Files
│       ├── registration/    # Login/Signup templates
│       └── stories/         # Game interface templates
│
└── flask-api/               # BACKEND: Game Logic API
    ├── Dockerfile           # Instructions to build the Flask image
    ├── run.py               # Entry point to start the Flask server
    ├── requirements.txt     # Python dependencies for Flask
    │
    ├── app/                 # Application Package
    │   ├── __init__.py      # Initializes the app and DB connection
    │   ├── models.py        # Database models for Story Nodes
    │   └── routes.py        # API endpoints (e.g., /get-story/<id>)
    │
    └── instance/            # Instance-specific files
        └── flask-db.sqlite  # Story content database
