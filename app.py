from flask import Flask, render_template, request, redirect, url_for, session, flash
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

assignemnt_counter = 3456

app = Flask(__name__, template_folder='assignmeant_app/static/templates', static_folder='static')
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
    # db.drop_all()
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
        student = Student(username=student_form.username.data, password=hashed_password, role='student', past_scores=[random.randint(1, 100), random.randint(1,100)], interests=student_form.interests.data)
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
    teacher = User.query.filter_by(username=session['username']).first()

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

            assignment_file_name = f'assignment_{assignemnt_counter}.json'    
            filepath = os.path.join(upload_folder, assignment_file_name)
            file.save(filepath)
        num_questions_requested = request.form.get('number_of_questions')

        assign_assignment(num_questions = num_questions_requested, students = students, teacher = teacher, path = filepath)
        print(f"Assigned {num_questions_requested} questions to {len(students)} students")
        return redirect(url_for('dashboard'))

    return render_template('assign.html', username=session['username'], students=students)

def assign_assignment(num_questions, students, teacher, path):
    global assignemnt_counter
    data = {}
    # data['title'] = 'Chapter 1 Questions'
    data["number_of_questions"] = num_questions
    data["students"] = []
    student_detail = {}
    for student in students:
        student_detail["student_id"] = student.id
        student_detail["interests"] = student.interests.split(',')
        student_detail["past_scores"] = student.past_scores
        data["students"].append(student_detail)

        # clear student_detail
        student_detail = {}
    print(data)

    file_path = f'./assignmeant_app/static/user.json'

    with open(file_path, 'w') as file:
        json.dump(data, file)
    
    # Get response from gpt regarding the assignments

    assignments_response = GPT_generate_questions(path, file_path)
    print(assignments_response)
    with open("ML_zone/cache.json", 'w') as file:
       json.dump(assignments_response, file)

    # with open("ML_zone/cache.json", 'r') as file:
    #     assignments_response = json.load(file)

    for curr_id, questions in assignments_response.items():
        # get numeric student id from string
        student_id = int(''.join([char for char in curr_id if char.isdigit()]))
        print(f"Returned Student ID: {student_id}")
        student = Student.query.filter_by(id=student_id).first()
        if not student:
            print('Student not found')
            continue
        # save questions in json file
        path = f'./assignmeant_app/static/assignments/assignment_{assignemnt_counter}.json'

        assignemnt_counter = assignemnt_counter + 1

        with open(path, 'w') as file:
            json.dump([{"title": "New Chapter 1 Questions", "questions": questions}], file)
        assignment = Assignment(
            title=f'New Chapter 1 Questions',
            file_path=  path,
            assigned_to_id= student.id,
            assigned_by_id= teacher.id
            )
        print('Assignment created')
        db.session.add(assignment)
    db.session.commit()


@app.route('/view_assignment/<int:assignment_id>', methods=['GET', 'POST'])
def view_assignment(assignment_id):
    # Check if user is logged in
    if 'username' not in session:
        flash("Please log in to view the assignment.", "warning")
        return redirect(url_for('login'))

    # Fetch the assignment from the database using the given assignment_id
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    print("This is the assignment file path:", assignment.file_path)
    
    # Load the JSON file
    with open(assignment.file_path, 'r') as file:
        assignment_data = json.load(file)
    
    assignment_title = assignment_data[0]['title']
    assignment_questions = assignment_data[0]['questions']
    # answers = [assignment_data[0]['questions'][i]['correct_answer'] for i in range(1,17)]
    
    print("Reached here")
    # If a POST request is made, process the form submission
    if request.method == 'POST':
        # Collect all answers
        answers = {}
        for question in assignment_questions:
            answer = request.form.get(f'answer_{question["id"]}')
            answers[question["id"]] = answer

        assignemnt_socre = calculate_score(assignment_questions, answers)
        print("Assignment Score:", assignemnt_socre)

        # Print user's answers to the console (for debugging purposes)
        print("User's answers:", answers)

        # You might want to save the answers or calculate the score here
        
        flash("Your answers have been submitted.", "success")
        return redirect(url_for('index'))

    print("Did not receive a POST request.")

    # Render the assignment viewing template with the assignment details
    return render_template('view_assignment.html', 
                           username=session['username'], 
                           assignment_title=assignment_title,
                           assignment_questions=assignment_questions)


def calculate_score(assignment_questiosn, answers):
    score = 0
    for question in assignment_questiosn:
        if answers[question['id']] == question['correct_answer']:
            score += 1
    return score

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

