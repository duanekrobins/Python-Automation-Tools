import os
import json
import pandas as pd
import openpyxl

# Header comment block
# Script Name: parse_test_scripts_to_tables.py
# Date: [Today's Date]
# Developer: Duane Robinson
# Purpose: This script automates the processing of JSON files containing automation
# sequence data. It reads each JSON, extracts essential script details and actions,
# and exports this information into a structured Excel file. This facilitates easy
# analysis and review of script actions and properties.

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
                step_association = scenario.get('stepAssociation')
                if step_association is not None:
                    step_association_value = step_association.get('value', 'No value')
                else:
                    step_association_value = 'No value'
                action_detail['step_association_value'] = step_association_value

            actions.append(action_detail)

    return script_info, actions

# Function to export script data to Excel, handling naming conventions for sheets and tables (DR)
def export_to_excel(scripts_data, output_file):
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        sheet_name_count = {}  # Keep track of duplicate sheet names (DR)
        table_name_count = {}  # Keep track of duplicate table names (DR)
        for script_name, actions in scripts_data.items():
            base_sheet_name = script_name[:31].replace('/', '_').replace('\\', '_').replace('*', '_').replace('?', '_').replace(':', '_').replace('[', '_').replace(']', '_').replace(' ', '_')
            sheet_name_count[base_sheet_name] = sheet_name_count.get(base_sheet_name, 0) + 1
            sheet = writer.book.create_sheet(title=f"{base_sheet_name}_{sheet_name_count[base_sheet_name]}")
            df = pd.DataFrame(actions)
            df.to_excel(writer, sheet_name=sheet.name, index=False)

# Function to process all JSON files in a directory and collect their data (DR)
def process_directory(directory):
    scripts_data = {}
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            json_data = load_json(file_path)
            script_info, actions = parse_script_data(json_data)
            scripts_data[script_info['name']] = actions
    return scripts_data

# Main block to run the script, asking for user input on directory and output file path (DR)
if __name__ == '__main__':
    directory = input("Enter the directory containing JSON files: ")
    output_file = input("Enter the path for the output Excel file: ")
    scripts_data = process_directory(directory)
    export_to_excel(scripts_data, output_file)

    print(f"Processed JSON files have been exported to {output_file}")
