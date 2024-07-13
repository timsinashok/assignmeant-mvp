import json

import json

def extract_student_data(content):
    data = {}
    lines = content.splitlines()
    
    current_key = None
    current_json = []
    inside_json_block = False

    for line in lines:
        if line.startswith("###"):
            if current_key is not None and current_json:
                # Join lines to form a valid JSON string
                joined_json = "".join(current_json).strip()
                print(f"Parsing JSON for key {current_key}: {joined_json}")
                try:
                    # Load JSON string into the dictionary
                    data[current_key] = json.loads(joined_json)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON for key {current_key}: {e}")
                    raise
            
            # Set new key and reset JSON content
            current_key = line.strip()[3:]
            current_json = []
        elif line.strip() == "```json":
            inside_json_block = True
        elif line.strip() == "```":
            inside_json_block = False
        elif inside_json_block:
            # Collect JSON content lines
            current_json.append(line)

    # Process the last block
    if current_key is not None and current_json:
        joined_json = "".join(current_json).strip()
        print(f"Parsing JSON for key {current_key}: {joined_json}")
        try:
            data[current_key] = json.loads(joined_json)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for key {current_key}: {e}")
            raise
    
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
   

