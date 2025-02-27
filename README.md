# AssignMeant

**AssignMeant** is a web-based application that generates personalized assignments for students using AI. Teachers can upload chapter PDFs, and the app leverages the Llama 3.18B model via Cerebras Inference to create questions tailored to each student’s interests and past performance. Built with Flask and MongoDB, the platform offers features like guided help and auto-grading to enhance learning.

## Features

- **AI-Generated Questions**: Questions are created from teacher-uploaded PDFs using the Llama 3.18B model through Cerebras Inference.
- **Personalization**: Assignments are tailored based on students' previous performance and interests.
- **Guided Help**: Students can access hints and guidance for solving questions. (Still in development)
- **Autograder**: Automatic grading for immediate feedback. (Still in development)
- **User Authentication**: Secure login and registration for both teachers and students.
- **Responsive Design**: Works seamlessly on desktop and mobile devices.

## Tech Stack

- **Backend**: Flask
- **Frontend**: HTML, CSS, JavaScript 
- **Database**: MongoDB
- **AI Model**: Llama 3.18B via Cerebras Inference
- **Version Control**: Git

## Prerequisites

- **Python 3.8+**
- **Flask** (installed via `pip install Flask`)
- **MongoDB** (local or cloud instance)
- **Cerebras API Key**

## Getting Started

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/timsinashok/assignmeant-mvp.git
   cd assignmeant-mvp
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
    MONGODB_URI = Your MongoDB URI
    cerebras_api = Your Cerebras API key
    TEMPLATE_FOLDER = assignmeant_app/new_static/templates
    STATIC_FOLDER = assignmeant_app/new_static
    SECRET_KEY=secret
   ```

2. **Ensure MongoDB is running**:

   If using a local instance, start the MongoDB service.

### Running the Application

1. **Start the Flask development server**:

   ```bash
   flask run
   ```

2. **Open your browser** and navigate to `http://127.0.0.1:5000`.

### Using the App

- **Teacher Workflow**:
  - Upload a PDF of a chapter and specify number of questions.
  - Assign questions generated by the AI to students.
- **Student Workflow**:
  - Log in to view personalized assignments.
  - Use the help feature for guidance and submit responses.
  - View graded feedback instantly.

# Contributors
This is a fun project we three of us started pursuing over Summer'24 and have been trying to improve over time. 

[Ashok Timsina](www.github.com/timsinashok)

[Manoj Dhakal](https://github.com/manoj-dhakal)

[Komal Neupane](https://github.com/komalnpn)
