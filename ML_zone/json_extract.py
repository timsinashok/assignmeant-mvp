import json

import re

def extract_student_data(content):
    try:
        # Parse the content string as JSON
        content_dict = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {e}")
        return {}  # Return an empty dictionary on error

    data = {}

    for key, questions in content_dict.items():
        student_key = key.strip()  # Ensuring no extra spaces
        data[student_key] = questions

    return data

def save_combined_json(data, output_file):
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Combined JSON saved to {output_file}")

def main(response_content):
    # Response content
    #response_content 
  
    combined_data = extract_student_data(response_content)
    
    print(f"Combined student data: {combined_data}")
    return combined_data
   

