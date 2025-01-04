from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson import ObjectId
import json
import os
import random
from datetime import datetime
from assignmeant_app.forms import RoleSelectionForm, StudentRegistrationForm, TeacherRegistrationForm

from dotenv import load_dotenv
load_dotenv()

from cerebras.cloud.sdk import Cerebras
cerebras_api = os.getenv('cerebras_api')

from ML_zone.main import GPT_generate_questions, grade_assignment

# Add colored print for better visibility
def status_print(message, status_type="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if status_type == "SUCCESS":
        print(f"\033[92m[{timestamp}] ✅ {message}\033[0m")
    elif status_type == "ERROR":
        print(f"\033[91m[{timestamp}] ❌ {message}\033[0m")
    elif status_type == "WARNING":
        print(f"\033[93m[{timestamp}] ⚠️ {message}\033[0m")
    else:
        print(f"\033[94m[{timestamp}] ℹ️ {message}\033[0m")


template_folder = os.getenv("TEMPLATE_FOLDER")
static_folder = os.getenv("STATIC_FOLDER")
secret_key = os.getenv("SECRET_KEY")


app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
app.secret_key = secret_key  

mongodb_uri =  os.getenv("MONGODB_URI")

# MongoDB configuration
try:
    client = MongoClient(mongodb_uri)
    db = client['assignment_db']
    status_print("Successfully connected to MongoDB", "SUCCESS")
except Exception as e:
    status_print(f"Failed to connect to MongoDB: {str(e)}", "ERROR")

# Login manager setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Please log in to access this page.'

class User(UserMixin):
    def __init__(self, user_data):
        self.user_data = user_data
        
    def get_id(self):
        return str(self.user_data['_id'])
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    @property
    def username(self):
        return self.user_data['username']
    
    @property
    def role(self):
        return self.user_data['role']
    
    @property
    def id(self):
        return str(self.user_data['_id'])

@login_manager.user_loader
def load_user(user_id):
    try:
        if not ObjectId.is_valid(user_id):
            status_print(f"Invalid ObjectId format: {user_id}", "ERROR")
            return None
        user_data = db.users.find_one({'_id': ObjectId(user_id)})
        if user_data:
            status_print(f"User loaded successfully: {user_data['username']}", "SUCCESS")
            return User(user_data)
        status_print(f"User not found for ID: {user_id}", "WARNING")
        return None
    except Exception as e:
        status_print(f"Error loading user: {str(e)}", "ERROR")
        return None

@app.route('/register', methods=['GET', 'POST'])
def register():
    role_form = RoleSelectionForm()
    if request.method == 'POST' and role_form.validate_on_submit():
        role = request.form.get('role')
        if role == 'student':
            return redirect(url_for('register_student'))
        elif role == 'teacher':
            return redirect(url_for('register_teacher'))
    return render_template('register.html', role_form=role_form)

@app.route('/register/student', methods=['GET', 'POST'])
def register_student():

    student_form = StudentRegistrationForm()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        interests = request.form.get('interests')

        status_print(f"Attempting to register new student: {username}")

        if db.users.find_one({'username': username}):
            status_print(f"Registration failed - Username already exists: {username}", "WARNING")
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register_student'))

        user_data = {
            'username': username,
            'password': generate_password_hash(password),
            'role': 'student',
            'past_scores': [random.randint(1, 100), random.randint(1, 100)],
            'interests': interests,
            'created_at': datetime.utcnow()
        }
        
        try:
            result = db.users.insert_one(user_data)
            if result.inserted_id:
                status_print(f"Student registered successfully: {username}", "SUCCESS")
                flash('You have successfully registered as a student!', 'success')
                return redirect(url_for('login'))
            else:
                status_print(f"Failed to insert new student: {username}", "ERROR")
                flash('Registration failed. Please try again.', 'danger')
                return redirect(url_for('register_student'))
        except Exception as e:
            status_print(f"Error during student registration: {str(e)}", "ERROR")
            flash('An error occurred during registration.', 'danger')
            return redirect(url_for('register_student'))

    return render_template('register_student.html', student_form=student_form)


@app.route('/register/teacher', methods=['GET', 'POST'])
def register_teacher():

    teacher_form = TeacherRegistrationForm()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        status_print(f"Attempting to register new teacher: {username}")

        if db.users.find_one({'username': username}):
            status_print(f"Registration failed - Username already exists: {username}", "WARNING")
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register_teacher'))

        user_data = {
            'username': username,
            'password': generate_password_hash(password),
            'role': 'teacher',
            'created_at': datetime.utcnow()
        }

        try:
            result = db.users.insert_one(user_data)
            if result.inserted_id:
                status_print(f"Teacher registered successfully: {username}", "SUCCESS")
                flash('You have successfully registered as a teacher!', 'success')
                return redirect(url_for('login'))
            else:
                status_print(f"Failed to insert new teacher: {username}", "ERROR")
                flash('Registration failed. Please try again.', 'danger')
                return redirect(url_for('register_teacher'))
        except Exception as e:
            status_print(f"Error during teacher registration: {str(e)}", "ERROR")
            flash('An error occurred during registration.', 'danger')
            return redirect(url_for('register_teacher'))

    return render_template('register_teacher.html', teacher_form=teacher_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        status_print(f"Login attempt for user: {username}")
        
        user_data = db.users.find_one({'username': username})
        
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            status_print(f"User logged in successfully: {username}", "SUCCESS")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            status_print(f"Failed login attempt for user: {username}", "WARNING")
            flash('Invalid username or password!', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    status_print(f"User logged out: {username}", "SUCCESS")
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    return render_template('index.html', username=current_user.username, role=current_user.role)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if current_user.role == 'teacher':
        students = list(db.users.find({'role': 'student'}))
        return render_template('teacher_dashboard.html', username=current_user.username, students=students)
    else:
        student_id = ObjectId(current_user.id)
        assignments = list(db.assignments.find({'assigned_to_id': student_id}))
        
        # Calculate scores
        scores = {}
        for assignment in assignments:
            submissions = list(db.submissions.find({'assignment_id': assignment['_id']}))
            scores[str(assignment['_id'])] = max([s['score'] for s in submissions]) if submissions else -1
            
        return render_template('student_dashboard.html', username=current_user.username, assignments=assignments, scores=scores, enumerate=enumerate)

@app.route('/view_student/<student_id>', methods=['GET', 'POST'])
@login_required
def view_student(student_id):
    if not ObjectId.is_valid(student_id):
        flash('Invalid student ID', 'danger')
        print("Invalid student ID")
        return redirect(url_for('dashboard'))
    print("Valid student ID")
    student = db.users.find_one({'_id': ObjectId(student_id)})
    print(student)
    if not student:
        flash('Student not found', 'danger')
        return redirect(url_for('dashboard'))
    
    print("Student found")
    assignments = list(db.assignments.find({'assigned_to_id': ObjectId(student_id)}))
    print("Assignments found")
    return render_template('view_student.html', student=student, assignments=assignments)


@app.route('/view_assignment/<assignment_id>', methods=['GET', 'POST'])
@login_required
def view_assignment(assignment_id):
    if not ObjectId.is_valid(assignment_id):
        flash('Invalid assignment ID', 'danger')
        return redirect(url_for('dashboard'))
        
    assignment = db.assignments.find_one({'_id': ObjectId(assignment_id)})
    print(assignment)
    if not assignment:
        flash('Assignment not found', 'danger')
        return redirect(url_for('dashboard'))
    
    assignment_title = assignment.get('name')
    assignment_questions = assignment.get('questions')

    print(assignment_questions)

    if request.method == 'POST':
        answers = {
            str(question['id']): request.form.get(f'answer_{question["id"]}') 
            for question in assignment_questions
        }
        
        score = grade_assignment(assignment_questions, answers)
        print('score: ', score)

        submission_data = {
            'user_id': ObjectId(current_user.id),
            'assignment_id': ObjectId(assignment_id),
            'user_answer': answers,
            'score': score,  # Implement scoring logic
            'submitted_at': datetime.utcnow()
        }
        
        db.submissions.insert_one(submission_data)
        flash("Your answers have been submitted.", "success")
        return redirect(url_for('index'))

    submission = db.submissions.find_one({
        'assignment_id': ObjectId(assignment_id)
    })

    if current_user.role == 'teacher':
        return render_template(
            'view_assignment_teacher.html',
            assignment_title=assignment_title,
            assignment_questions=assignment_questions,
            submission=submission
        )

    return render_template(
        'view_assignment.html',
        username=current_user.username,
        assignment_title=assignment_title,
        assignment_questions=assignment_questions,
        submission=submission
    )

@app.route('/assign', methods=['GET', 'POST'])
@login_required
def assign():
    if current_user.role != 'teacher':
        status_print(f"Unauthorized access attempt to assign by: {current_user.username}", "WARNING")
        return redirect(url_for('index'))

    filepath = None  # Initialize filepath to None

    if request.method == 'POST':
        status_print(f"Teacher {current_user.username} attempting to create new assignment")

        if 'file' not in request.files:
            status_print("No file uploaded", "WARNING")
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            status_print("Empty file selected", "WARNING")
            flash('No selected file')
            return redirect(request.url)

        assignment_file_name = f'assignment_{datetime.now().timestamp()}.pdf'
        upload_folder = os.path.join(app.root_path, 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        filepath = os.path.join(upload_folder, assignment_file_name)
        if file:
            try:
                file.save(filepath)
                status_print(f"Assignment file saved: {assignment_file_name}", "SUCCESS")

                num_questions = int(request.form.get('number_of_questions'))

                students = list(db.users.find({'role': 'student'}))
                data = {"number_of_questions": num_questions, "students": []}
                for student in students:
                    data["students"].append({
                        "student_id": str(student["_id"]),
                        "interests": student["interests"].split(','),
                        "past_scores": student["past_scores"]
                    })
                query = None
                print(data)
                questions = GPT_generate_questions(filepath, data)
                created_count = 0
                for student in students:
                    query1 = "Student ID: " + str(student['_id'])
                    query2 =  str(student['_id'])
                    if query1 in questions:
                        query = query1
                    else:
                        query = query2
                    assignment_name = "Assignment" + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    assignment_data = {
                        'name' : assignment_name,
                        'assigned_to_id': student['_id'],
                        'teacher_id': ObjectId(current_user.id),
                        'file_path': filepath,
                        'created_at': datetime.utcnow(),
                        'questions': questions[query]
                    }
                    result = db.assignments.insert_one(assignment_data)
                    if result.inserted_id:
                        created_count += 1

                status_print(f"Created {created_count} assignments successfully", "SUCCESS")
                flash('Assignment created successfully!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                status_print(f"Error creating assignment: {str(e)}", "ERROR")
                flash('Error creating assignment.', 'danger')
                return redirect(url_for('dashboard'))

    students = list(db.users.find({'role': 'student'}))
    teachers = list(db.users.find({'role': 'teacher'}))

    return render_template('assign.html', username=current_user.username, students=students, teachers=teachers, path=filepath)# Add similar status prints to other routes as needed...

app.route('/get_help', methods=['GET', 'POST'])
def get_help():
    return render_template('get_help.html')

@app.route('/get_help', methods=['GET'])
def get_response():
    print("endpoint_hit")
    question = request.args.get('question')
    client = Cerebras(api_key=cerebras_api)
    message = [{'role': 'user', 'content': question}]
    response = client.chat.completions.create(
        model="llama3.1-8b",
        messages=message
    )
    response = response.choices[0].message.content
    print(response)
    return response

if __name__ == '__main__':
    status_print("Starting Flask application", "SUCCESS")
    app.run(debug=True, port=5001)