import os
from ML_zone.config import read_api_config
from ML_zone.pdf_processor import extract_text_from_pdf
#from gpt_api import send_text_to_gpt_api, print_readable_response
from ML_zone.student_processor import process_students
from openai import OpenAI
import json

def process_pdf_with_gpt4o(pdf_filename):
    try:
        pdf_path = os.path.join(os.getcwd(), pdf_filename)
        pdf_text = extract_text_from_pdf(pdf_path)
       
        return pdf_text
    
    except Exception as e:
        print(f"An error occurred: {e}")


def GPT_generate_questions(pdf_filename, dictionary_path):
    
    with open(dictionary_path, 'r') as json_file:
        data = json.load(json_file)

    num_of_questions = data["number_of_questions"]

    with open('student_data.json', 'w') as json_file:
        json.dump(data["students"], json_file, indent=4)

    additional_messages = [
        {'role': 'assistant', 'content': f"Play the role of a teacher assigning assignments for their students for me. I will first pass the text to base the questions on, then I will pass the student data(name, interests and past quiz scores) to generate the questions. The questions should be primarlily based on the text passed, and then should be strictly linked to the student interests. The difficulty level should be based on the past quiz scores. The questions for each student should be a json format where for each question, there are these keys: 'id', 'question', 'correct_answer'. For now, assign {num_of_questions} questions for each student. Before giving the json file for each student just mention the id of the student and nothing else strictly."}  
    ]
    config_file = 'ML_zone/config.txt'  # Replace with the path to your config.txt file

    # Process student data
    json_file = 'student_data.json'  # Replace with the path to your JSON file with student data
    client = OpenAI(api_key=read_api_config(config_file))
   
    message_2 = [{'role': 'user', 'content': f'Following is the text to strictly base all the questions on: {process_pdf_with_gpt4o(pdf_filename)}'}]
    additional_messages.extend(message_2)
    return process_students(json_file, client, additional_messages)

