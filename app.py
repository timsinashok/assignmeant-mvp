from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from assignmeant_app.models import db, User, Assignment, Submission, Student, Teacher
import json
import os
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from assignmeant_app.forms import RoleSelectionForm, StudentRegistrationForm, TeacherRegistrationForm
import random
from ML_zone.main import GPT_generate_questions
from assignmeant_app.utils.Helpers.helperFunctions import assign_assignment, calculate_score, ai_calculate_score

from ML_zone.ai71_helper import get_response

assignemnt_pdf_counter = 3456

app = Flask(__name__, template_folder='assignmeant_app/new_static/templates', static_folder='assignmeant_app/new_static')
app.secret_key = 'supersecretkey'  # Replace with a secure key in production

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')

# Migrate the database
migrate = Migrate(app, db)

# Set the login view - this is the view to redirect to for login
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Please log in to access this page.'

# Create the database and tables
with app.app_context():
    #db.drop_all()
    db.create_all()

# Load the user object from the user ID stored in the session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route for user registration
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

# Route for student registration
@app.route('/register/student', methods=['GET', 'POST'])
def register_student():
    student_form = StudentRegistrationForm()

    if request.method == 'POST' and student_form.validate_on_submit():
        existing_user = User.query.filter_by(username=student_form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register_student'))

        hashed_password = generate_password_hash(student_form.password.data)
        student = Student(username=student_form.username.data, password=hashed_password, role='student', past_scores=[random.randint(1, 100), random.randint(1,100)], interests=student_form.interests.data)
        db.session.add(student)
        db.session.commit()
        flash('You have successfully registered as a student!', 'success')
        return redirect(url_for('login'))

    return render_template('register_student.html', student_form=student_form)

# Route for teacher registration
@app.route('/register/teacher', methods=['GET', 'POST'])
def register_teacher():
    teacher_form = TeacherRegistrationForm()

    if request.method == 'POST' and teacher_form.validate_on_submit():
        existing_user = User.query.filter_by(username=teacher_form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register_teacher'))

        hashed_password = generate_password_hash(teacher_form.password.data)
        teacher = Teacher(username=teacher_form.username.data, password=hashed_password, role='teacher')
        db.session.add(teacher)
        db.session.commit()
        flash('You have successfully registered as a teacher!', 'success')
        return redirect(url_for('login'))

    return render_template('register_teacher.html', teacher_form=teacher_form)

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Route for logging out
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Global home page
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html', username=current_user.username, role=current_user.role)

# Dashboard route
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if current_user.role == 'teacher':
        students = User.query.filter_by(role='student').all()
        return render_template('teacher_dashboard.html', username=current_user.username, students=students)
    else:
        student = current_user
        assignments = Assignment.query.filter_by(assigned_to_id=student.id).all()
        scores = {assignment.id: get_max_score(Submission.query.filter_by(assignment_id=assignment.id).all()) if Submission.query.filter_by(assignment_id=assignment.id).all() else -1 for assignment in assignments}
        return render_template('student_dashboard.html', username=current_user.username, assignments=assignments, scores=scores, enumerate=enumerate)

get_max_score = lambda submissions: max([submission.score for submission in submissions])

# View student route
@app.route('/view_student/<int:student_id>', methods=['GET', 'POST'])
@login_required
def view_student(student_id):
    student = User.query.filter_by(id=student_id).first()
    assignments = Assignment.query.filter_by(assigned_to_id=student.id).all()
    return render_template('view_student.html', student=student, assignments=assignments)

# Assign route to assign assignment by teacher
@app.route('/assign', methods=['GET', 'POST'])
@login_required
def assign():
    global assignemnt_pdf_counter
    if current_user.role != 'teacher':
        return redirect(url_for('index'))

    students = User.query.filter_by(role='student').all()
    teacher = current_user

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file:
            upload_folder = os.path.join(app.root_path, 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            assignment_file_name = f'assignment_{assignemnt_pdf_counter}.pdf'
            filepath = os.path.join(upload_folder, assignment_file_name)
            print("Saved pdf here: ", filepath)
            file.save(filepath)
            assignemnt_pdf_counter += 1
        
        num_questions_requested = request.form.get('number_of_questions')
        assign_assignment(num_questions=num_questions_requested, students=students, teacher=teacher, path=filepath)
        return redirect(url_for('dashboard'))

    return render_template('assign.html', username=current_user.username, students=students)

# View assignment route to view specific assignment, handles assignment view for teacher and student
@app.route('/view_assignment/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def view_assignment(assignment_id):
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    with open(assignment.file_path, 'r') as file:
        assignment_data = json.load(file)
    
    assignment_title = assignment_data[0]['title']
    assignment_questions = assignment_data[0]['questions']

    if request.method == 'POST':
        answers = {question["id"]: request.form.get(f'answer_{question["id"]}') for question in assignment_questions}
        #assignment_score = calculate_score(assignment_questions, answers)
        assignment_score = ai_calculate_score(assignment_questions, answers)

        submission = Submission(user_id=current_user.id, assignment_id=assignment_id, user_answer=answers, score=assignment_score)
        db.session.add(submission)
        db.session.commit()
        
        flash("Your answers have been submitted.", "success")
        return redirect(url_for('index'))

    submission = Submission.query.filter_by(assignment_id=assignment_id).first()

    if current_user.role == 'teacher':
        return render_template('view_assignment_teacher.html', assignment_title=assignment_title, assignment_questions=assignment_questions, submission=submission)

    return render_template('view_assignment.html', username=current_user.username, assignment_title=assignment_title, assignment_questions=assignment_questions, submission=submission)

@app.route('/get_response')
def get_response_route():
    # Get the question parameter from the query string
    question = request.args.get('question')

    additional_messages = [
        {'role': 'assistant', 'content': f"Play the role of a helpful teacher and guide a student on this questions."},  
    ]

    prompt = f"The student is stuck on this question and needs help. The question is: {question} \n Help the sutdent with with question without giving full solution but a good direction to the solution."


    print("Prompt:", prompt)
    prompt += "Please provide short and concise hint that will help student solve the problem. \n"


    message_2 = [{'role': 'user', 'content': prompt}]
    additional_messages.extend(message_2)

    response = get_response(additional_messages)
    print("Response From ai71:", response)
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5001)


