# mvp
hello manoj is the CDO of this company. what is a CDO you might ask, keep thinking, I love your curiosity. muah.


# Assignment Platform

![Assignment Platform]([https://github.com/assignMeant/mvp/blob/main/assignmeant_app/static/images/logo.png])

**Assignment Platform** is a web-based application for managing assignments between teachers and students. It allows teachers to assign tasks and students to view and submit their responses. The platform is built using Flask and SQLAlchemy, providing a robust and scalable framework for educational environments.

## Features

- **User Authentication**: Secure login and registration for both teachers and students.
- **Assignment Management**: Teachers can create and assign tasks to students.
- **Question Handling**: Support for different question types, including text responses.
- **Responsive Design**: A user-friendly interface that works on both desktop and mobile devices.
- **Real-Time Updates**: Immediate feedback and scoring for student submissions.
- **Profile Management**: Students can view their past scores and track their progress.

## Tech Stack

- **Backend**: Flask, SQLAlchemy
- **Frontend**: HTML, CSS (Bootstrap), JavaScript
- **Database**: SQLite (development), PostgreSQL/MySQL (production)
- **Version Control**: Git

## Prerequisites

- **Python 3.8+**
- **Flask** (installed via `pip install Flask`)
- **SQLAlchemy** (installed via `pip install SQLAlchemy`)
- **Bootstrap** (included via CDN)
- **Font Awesome** (included via CDN)

## Getting Started

### Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/yourusername/assignment-platform.git
    cd assignment-platform
    ```

2. **Create a virtual environment**:

    ```bash
    python -m venv venv
    ```

3. **Activate the virtual environment**:

    - **On Windows**:
      ```bash
      venv\Scripts\activate
      ```
    - **On macOS/Linux**:
      ```bash
      source venv/bin/activate
      ```

4. **Install the required packages**:

    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1. **Set environment variables**:

    Create a `.env` file in the root directory and add the following:

    ```env
    FLASK_APP=run.py
    FLASK_ENV=development
    SECRET_KEY=your_secret_key
    SQLALCHEMY_DATABASE_URI=sqlite:///assignment.db
    ```

2. **Initialize the database**:

    ```bash
    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade
    ```

### Running the Application

1. **Start the Flask development server**:

    ```bash
    flask run
    ```

2. **Open your browser** and navigate to `http://127.0.0.1:5000`.

### Creating Users

- **Register** as a new user.
- **Log in** with your credentials.

### Creating and Viewing Assignments

- **Teachers** can create assignments and assign them to students.
- **Students** can view their assigned tasks and submit responses.

## Directory Structure

```plaintext
assignment-platform/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── view_assignment.html
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   ├── forms.py
│   ├── utils.py
│
├── migrations/
│
├── venv/
│
├── .env
├── requirements.txt
├── README.md
├── run.py
└── config.py
