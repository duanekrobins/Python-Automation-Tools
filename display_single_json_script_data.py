import json

# Header comment block
# Script Name: parse_test_script.py
# Date: [Today's Date]
# Developer: Duane Robinson
# Purpose: This script is designed to load a single JSON file specified by the user,
# parse the data to extract automation script information and action details,
# and then display this extracted data directly in the console in a structured JSON format.
# It is useful for quick checks and debugging of script data.

# Function to load a JSON file and return its content (DR)
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to parse script data from JSON and extract relevant details (DR)
def parse_script_data(json_data):
    script_info = {
        'name': json_data.get('automationSequence', {}).get('name', 'No name'),
        'description': json_data.get('automationSequence', {}).get('description', 'No description')
    }

    actions = []
    for sequence in json_data.get('sequenceList', []):
        for scenario in sequence.get('scenarioFlowList', []):
            action_detail = {
                'action_name': scenario.get('action_name', 'No action name'),
                'english_text': scenario.get('english_text', 'No English text'),
                'action_code': scenario.get('action_code', 'No action code'),
                'name': scenario.get('name', 'No name')
            }

            if action_detail['action_name'] == "Enter Text":
                step_association_value = scenario.get('stepAssociation', {}).get('value', 'No value')
                action_detail['step_association_value'] = step_association_value

            actions.append(action_detail)

    return script_info, actions

# Main block to run the script, asking for user input on JSON file path (DR)
if __name__ == '__main__':
    file_path = input("Enter the path to your JSON file: ")
    json_data = load_json(file_path)
    script_info, actions = parse_script_data(json_data)

    print("Script Information:")
    print(json.dumps(script_info, indent=4))
    print("\nActions:")
    print(json.dumps(actions, indent=4))
