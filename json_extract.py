import json

def extract_student_data(content):
    students_data = {}
    student_sections = content.split('```json')
    
    for section in student_sections:
        if '### ' in section:
            name_start = section.find('### ') + 4
            name_end = section.find('\n', name_start)
            student_name = section[name_start:name_end].strip()
            
            json_start = section.find('[')
            json_end = section.find(']', json_start) + 1
            
            if json_start != -1 and json_end != -1:
                student_json_str = section[json_start:json_end].strip()
                try:
                    student_data = json.loads(student_json_str)
                    students_data[student_name] = student_data
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON for student {student_name}: {e}")
    
    return students_data

def save_combined_json(data, output_file):
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Combined JSON saved to {output_file}")

def main(response_content):
    # Response content
    response_content 
    combined_data = extract_student_data(response_content)
    save_combined_json(combined_data, 'combined_students_data.json')

