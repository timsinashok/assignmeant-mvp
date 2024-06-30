from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Base User class
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': role
    }

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

# Association table for many-to-many relationship between Teachers and Students
teacher_student_association = db.Table('teacher_student',
    db.Column('teacher_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('student_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# Teacher class inheriting from User
class Teacher(User):
    students = db.relationship(
        'Student',
        secondary=teacher_student_association,
        primaryjoin='Teacher.id == teacher_student.c.teacher_id',
        secondaryjoin='Student.id == teacher_student.c.student_id',
        back_populates='teachers'
    )

    __mapper_args__ = {
        'polymorphic_identity': 'teacher',
    }

    def __repr__(self):
        return f'<Teacher {self.username}>'

# Student class inheriting from User
class Student(User):
    interests = db.Column(db.String(500))  # Store interests as a comma-separated string
    past_scores = db.Column(db.JSON)  # Store past scores as a JSON list
    teachers = db.relationship(
        'Teacher',
        secondary=teacher_student_association,
        primaryjoin='Student.id == teacher_student.c.student_id',
        secondaryjoin='Teacher.id == teacher_student.c.teacher_id',
        back_populates='students'
    )

    __mapper_args__ = {
        'polymorphic_identity': 'student',
    }

    def __repr__(self):
        return f'<Student {self.username}>'

# Modified Assignment class
class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    questions = db.Column(db.JSON, nullable=False)
    assigned_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Teacher who assigned the task
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Student who receives the task

    # Relationships to the User table
    assigned_by = db.relationship('Teacher', foreign_keys=[assigned_by_id], backref='assigned_tasks')
    assigned_to = db.relationship('Student', foreign_keys=[assigned_to_id], backref='received_assignments')

    def __repr__(self):
        return f'<Assignment {self.title} assigned by {self.assigned_by.username} to {self.assigned_to.username}>'

# Submission class
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    user_answer = db.Column(db.JSON, nullable=False)
    score = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref=db.backref('submissions', lazy=True))
    assignment = db.relationship('Assignment', backref=db.backref('submissions', lazy=True))

    def __repr__(self):
        return f'<Submission {self.id} by User {self.user_id}>'
