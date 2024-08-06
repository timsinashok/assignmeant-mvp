import json
from assignmeant_app.models import db, Assignment, Student
from ML_zone.main import GPT_generate_questions
assignemnt_counter = 3456

from ML_zone.ai71_helper import get_response

# Assign assignment helper function
def assign_assignment(num_questions, students, teacher, path):
    global assignemnt_counter
    data = {"number_of_questions": num_questions, "students": []}
    for student in students:
        data["students"].append({"student_id": student.id, "interests": student.interests.split(','), "past_scores": student.past_scores})

    # file_path = f'./assignmeant_app/new_static/user.json'
    # with open(file_path, 'w') as file:
    #     json.dump(data, file)
    
    # with open("ML_zone/cache.json", 'r') as file:
    #     assignments_response = json.load(file)
    assignments_response = GPT_generate_questions("temp.pdf",data)
    
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


def ai_calculate_score(assignment_questions, answers):
    # make list of answers
    questions = [question['question'] for question in assignment_questions]
    correct_ans = [question['correct_answer'] for question in assignment_questions]
    user_ans = [answer for answer in answers.values()]

    additional_messages = [
        {'role': 'assistant', 'content': f"Play the role of a teacher grading assignments of the students. I will pass question, correct answer and the student's answer for each questions and you have to grade each question out of 10. "},  
    ]

    role = "You are a professor trying to grade an assignment. \n"
    prompt = "I want you to grade an assignment based on given questions, correct answer and user's answer. Each question is of 10 point and you can score 1 to 10 for each question. \n"

    for i in range(len(questions)):
        prompt += f"Question: {questions[i]}\nCorrect Answer: {correct_ans[i]}\nStudents's Answer: {user_ans[i]}\n\n"

    print("Prompt:", prompt)
    prompt += "Please provide just the the score for this assignment. Do not show any calculation or stepe. Just give final score in number as response. Strictly give one final score as response. \n"


    message_2 = [{'role': 'user', 'content': prompt}]
    additional_messages.extend(message_2)

    response = get_response(additional_messages)
    print("Response From ai71:", response)
    return int(response)