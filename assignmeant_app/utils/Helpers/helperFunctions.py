import json
from assignmeant_app.models import db, Assignment, Student

assignemnt_counter = 3456

# Assign assignment helper function
def assign_assignment(num_questions, students, teacher, path):
    global assignemnt_counter
    data = {"number_of_questions": num_questions, "students": []}
    for student in students:
        data["students"].append({"student_id": student.id, "interests": student.interests.split(','), "past_scores": student.past_scores})

    file_path = f'./assignmeant_app/new_static/user.json'
    with open(file_path, 'w') as file:
        json.dump(data, file)
    
    with open("ML_zone/cache.json", 'r') as file:
        assignments_response = json.load(file)

    for curr_id, questions in assignments_response.items():
        student_id = int(''.join([char for char in curr_id if char.isdigit()]))
        student = Student.query.filter_by(id=student_id).first()
        if not student:
            continue

        path = f'./assignmeant_app/new_static/assignments/assignment_{assignemnt_counter}.json'
        assignemnt_counter += 1
        with open(path, 'w') as file:
            json.dump([{"title": "New Chapter 1 Questions", "questions": questions}], file)
        
        assignment = Assignment(title=f'New Chapter 1 Questions', file_path=path, assigned_to_id=student.id, assigned_by_id=teacher.id)
        db.session.add(assignment)
    db.session.commit()

# Helper function to calculate score
def calculate_score(assignment_questions, answers):
    score = sum(1 for question in assignment_questions if answers[question['id']] == question['correct_answer'])
    return score