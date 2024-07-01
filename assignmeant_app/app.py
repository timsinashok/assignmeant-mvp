from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Assignment, Submission, Student
import json
import os
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from forms import RoleSelectionForm, StudentRegistrationForm, TeacherRegistrationForm

app = Flask(__name__, template_folder='static/templates', static_folder='static')
app.secret_key = 'supersecretkey'  # Replace with a secure key in production

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')

migrate = Migrate(app, db)

login_manager = LoginManager(app)

# Set the login view - this is the view to redirect to for login
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Please log in to access this page.'


# Create the database and tables
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Utility function to load assignments from a JSON file
def load_assignments():
    try:
        with open(os.path.join(app.config['UPLOAD_FOLDER'], 'assignments.json'), 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    
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

    if request.method == 'POST' and student_form.validate_on_submit():
        hashed_password = generate_password_hash(student_form.password.data)
        student = User(username=student_form.username.data, password=hashed_password, role='student')
        db.session.add(student)
        db.session.commit()
        flash('You have successfully registered as a student!', 'success')
        return redirect(url_for('login'))

    return render_template('register_student.html', student_form=student_form)

@app.route('/register/teacher', methods=['GET', 'POST'])
def register_teacher():
    teacher_form = TeacherRegistrationForm()

    if request.method == 'POST' and teacher_form.validate_on_submit():
        hashed_password = generate_password_hash(teacher_form.password.data)
        teacher = User(username=teacher_form.username.data, password=hashed_password, role='teacher')
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

        if user and user.check_password(password):
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!')
            return redirect(url_for('login'))

    return render_template('login.html')

# Route for logging out
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

# global home page
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'], role = session['role'])

@app.route('/dashboard', methods=['GET', 'POST'])
# @login_required
def dashboard():
    # check if user is teacher or student
    if session.get('role') == 'teacher':
        # get list of students based on teacher id
        students = User.query.filter_by(role='student').all()
        return render_template('teacher_dashboard.html', username=session['username'], students=students)
    else:
        # get list of assignments
        student = User.query.filter_by(username=session['username']).first()
        assignments = Assignment.query.filter_by(assigned_to_id =student.id).all()
        return render_template('student_dashboard.html', username=session['username'], assignments=assignments) 
    
@app.route('/assign', methods=['GET', 'POST'])
def assign():
    if 'username' not in session or session.get('role') != 'teacher':
        return redirect(url_for('index'))

    students = User.query.filter_by(role='student').all()
    assignments = Assignment.query.all()

    if request.method == 'POST':
        student_id = request.form.get('student')
        assignment_id = request.form.get('assignment')
        student = User.query.get(student_id)
        assignment = Assignment.query.get(assignment_id)
        student.assignments.append(assignment)
        db.session.commit()
        flash('Assignment added successfully!')
        return redirect(url_for('dashboard'))

    return render_template('assign.html', username=session['username'], students=students, assignments=assignments)

# # Home page displaying list of assignments
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if 'username' not in session:
#         return redirect(url_for('login'))
#     assignments = Assignment.query.all()
#     score = None
#     total_questions = sum(len(a.questions) for a in assignments)

#     if request.method == 'POST':
#         score = 0
#         for assignment in assignments:
#             assignment_id = assignment.id
#             user_answer = request.form.get(f'answer_{assignment_id}')
#             correct_answer = assignment.questions.get('correct_answer')
            
#             if user_answer.strip().lower() == correct_answer.strip().lower():
#                 score += 1

#             submission = Submission(user_id=session['user_id'], assignment_id=assignment_id, user_answer=user_answer, score=score)
#             db.session.add(submission)
#             db.session.commit()

#         return render_template('index.html', assignments=assignments, score=score, total_questions=total_questions, username=session['username'])

#     return render_template('index.html', assignments=assignments, username=session['username'])

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session or session.get('role') != 'teacher':
        return redirect(url_for('index'))

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
            # Ensure the upload directory exists
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            filepath = os.path.join(upload_folder, 'assignments.json')
            file.save(filepath)
            
            assignments_data = load_assignments()

            for assignment_data in assignments_data:
                assignment = Assignment(
                    title=assignment_data['title'],
                    questions=assignment_data['questions']
                )
                db.session.add(assignment)
                db.session.commit()

            flash('Assignments uploaded successfully!')
            return redirect(url_for('index'))

    return render_template('upload.html', username=session['username'])

if __name__ == '__main__':
    app.run(debug=True, port = 5001)

