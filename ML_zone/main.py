import os
from ML_zone.pdf_processor import extract_text_from_pdf
#from gpt_api import send_text_to_gpt_api, print_readable_response
from ML_zone.student_processor import process_students
from cerebras.cloud.sdk import Cerebras
import json

from dotenv import load_dotenv
load_dotenv()

cerebras_api = os.getenv('cerebras_api')

def process_pdf_with_gpt4o(pdf_filename):
    try:
        pdf_path = os.path.join(os.getcwd(), pdf_filename)
        pdf_text = extract_text_from_pdf(pdf_path)
       
        return pdf_text
    
    except Exception as e:
        print(f"An error occurred: {e}")

def grade_assignment(assignment_questions, user_answers):
    client = Cerebras(api_key=cerebras_api)
    rule = f"**Grade the assignment out of 10 and Strictly give the response in this format. Score = score/10**"
    message = [{'role': 'user', 'content': f"Following is the assignment and the correct anserws: {assignment_questions}', your job is to grade the answers provided by the students: {user_answers}"}]
    response = client.chat.completions.create(
        model="llama3.1-8b",
        messages=message
    )

    # clean and get the integer score
    response = response.choices[0].message.content
    score = response.split('=')[1].strip().split('/')[0].strip()

    return score
    
    


def GPT_generate_questions(pdf_filename, data):
    
    print("Pdf file name = ", pdf_filename)
    print("Data = ", data)
    num_of_questions = data["number_of_questions"]

    with open('student_data.json', 'w') as json_file:
        json.dump(data["students"], json_file, indent=4)
    
    # JSON format for the questions
    json_format = '''{
    "Student ID: student_id": [
        {
            "id": qn_id (starting from 1),
            "question": "question text",
            "correct_answer": "answer text"
        },
        {
            "id": qn_id,
            "question": "question text",
            "correct_answer": "answer text"
        }
    ],
    "Student ID: student_id": [
        {
            "id": qn_id,
            "question": "question text",
            "correct_answer": "answer text"
        },
        {
            "id": qn_id,
            "question": "question text",
            "correct_answer": "answer text"
        }
    ]
}'''

# Assistant prompt
    additional_messages = [
    {
        'role': 'assistant',
        'content': f"""
        I will provide a text and student data. Your task is to generate {num_of_questions} questions for each student based on the text and their interests/past quiz scores.

        The response must adhere strictly to the following JSON format, and there should be **no explanation or additional text outside of this format**:

        ```json
        {json_format}
        ```

        Rules:
        1. Ensure the JSON is valid and complete. Dictionaries must be inside **one single JSON object** for all students.
        2. Do not add any explanations, headers, or text outside the JSON.
        3. Ensure proper key-value pairs for 'id', 'question', and 'correct_answer'.
        4. If any data is missing, leave the value as an empty string ("").

        Generate exactly {{num_of_questions}} questions per student in this format.
        """
    }
]
    config_file = 'ML_zone/config.txt'  # Replace with the path to your config.txt file

    # Process student data
    json_file = 'student_data.json'  # Replace with the path to your JSON file with student data
    client = Cerebras(api_key=cerebras_api)

   
    message_2 = [{'role': 'user', 'content': f'Following is the text to strictly base all the questions on: {process_pdf_with_gpt4o(pdf_filename)}'}]
    additional_messages.extend(message_2)
    return process_students(json_file, client, additional_messages)


