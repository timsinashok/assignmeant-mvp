import json
from ML_zone.gpt_api import send_student_data_to_gpt, print_readable_response
def read_json_file(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    return data

def process_students(json_file, client, additional_messages):
    try:
        students = read_json_file(json_file)
        
        for student in students:
            collect_data(student, additional_messages)

        
        response = send_student_data_to_gpt(client, additional_messages)
        if response:
            final_questions = print_readable_response(response)
        else:
            print(f"Failed to process data for {student['student_name']}")

    except Exception as e:
        print(f"An error occurred: {e}")
    
    return final_questions

def collect_data(student_data, additional_messages):
    messages = [
        {'role': 'user', 'content': json.dumps(student_data)},
    ]
    additional_messages.extend(messages)