
import json
from ML_zone.json_extract import main

def send_student_data_to_gpt(client, additional_messages):
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=additional_messages,
        max_tokens=1000,
        temperature=0.3
    )

    return response

def print_readable_response(response):
    print("\nGPT-4 OpenAI API Response:\n")
    print("Response Content:")
    print(response.choices[0].message.content)
    return main(response.choices[0].message.content)

def extract_and_save_json(content, output_file):
    try:
        start_index = content.find('[')
        end_index = content.find(']', start_index + 1)

        if start_index == -1 or end_index == -1:
            raise ValueError("No JSON array found.")

        json_part = content[start_index:end_index + 1].strip()
        data = json.loads(json_part)

        with open(output_file, 'w') as file:
            json.dump(data, file, indent=4)

        print(f"JSON part saved to {output_file}")

    except Exception as e:
        print(f"Error extracting and saving JSON part: {e}")
