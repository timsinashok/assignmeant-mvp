import json
import re

def extract_student_data(content):
    """
    Extracts JSON data from a given content string.

    Args:
        content (str): The input text containing JSON data.

    Returns:
        dict: A parsed JSON object (since we expect a single JSON structure).
    """
    # Search for the JSON content in the response using regex
    match = re.search(r'\{.*\}', content, re.DOTALL)
    
    if match:
        try:
            # Parse the matched JSON string
            student_data = json.loads(match.group(0))
            return student_data
        except json.JSONDecodeError as e:
            print(f"Failed to parse the JSON: {e}")
            return None
    else:
        print("No JSON block found.")
        return None
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
   

