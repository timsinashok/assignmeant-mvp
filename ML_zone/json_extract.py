import json

def extract_student_data(content):
    students_data = {}
    # Split the content into sections where each section may contain a student ID and JSON data
    student_sections = content.split('```json')
    
    for section in student_sections:
        # Check if the section contains a student ID indicated by '### '
        if '### ' in section:
            # Extract the student ID
            name_start = section.find('###') + 4
            name_end = section.find('\n', name_start)
            student_id = section[name_start:name_end].strip()
            
            # Ensure the extracted ID is a valid number
            if student_id.isdigit():
                student_id = int(student_id)  # Convert to integer for better handling

                # Find the start and end of the JSON data
                json_start = section.find('[')
                json_end = section.find(']', json_start) + 1
                
                if json_start != -1 and json_end != -1:
                    # Extract the JSON string
                    student_json_str = section[json_start:json_end].strip()
                    try:
                        # Parse the JSON data
                        student_data = json.loads(student_json_str)
                        # Add the parsed data to the dictionary using the student ID as the key
                        students_data[student_id] = student_data
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON for student ID {student_id}: {e}")
            else:
                print(f"Warning: Invalid student ID '{student_id}' found in the content. Skipping this section.")
    
    return students_data

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
   

