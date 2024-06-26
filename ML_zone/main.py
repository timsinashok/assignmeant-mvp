import os
from config import read_api_config
from pdf_processor import extract_text_from_pdf
#from gpt_api import send_text_to_gpt_api, print_readable_response
from student_processor import process_students
from openai import OpenAI

def process_pdf_with_gpt4o(pdf_filename):
    try:
        pdf_path = os.path.join(os.getcwd(), pdf_filename)
        pdf_text = extract_text_from_pdf(pdf_path)
       
        return pdf_text
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    pdf_filename = 'temp.pdf'  # Replace with the actual name of your PDF file
    additional_messages = [
        {'role': 'assistant', 'content': "Play the role of a teacher assigning assignments for their students for me. I will first pass the text to base the questions on, then I will pass the student data(name, interests and past quiz scores) to generate the questions. The questions should be primarlily based on the text passed, and then should be strictly linked to the student interests. The difficulty level should be based on the past quiz scores. The questions for each student should be a json format where for each question, there are these keys: 'id', 'question', 'correct_answer'. For now, assign 2 questions for each student."}  
    ]
    config_file = 'config.txt'  # Replace with the path to your config.txt file

    # Process student data
    json_file = 'student_data.json'  # Replace with the path to your JSON file with student data
    client = OpenAI(api_key=read_api_config(config_file))
   
    message_2 = [{'role': 'user', 'content': f'Following is the text to strictly base all the questions on: {process_pdf_with_gpt4o(pdf_filename)}'}]
    additional_messages.extend(message_2)
    process_students(json_file, client, additional_messages)
