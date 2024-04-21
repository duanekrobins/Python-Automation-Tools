# Automation Script Data Parser and Excel Exporter
# Date: April 21, 2024
# Developer: Duane Robinson
# Purpose: This script processes directories of JSON files containing test automation data, 
#          extracting key details like script names, descriptions, and action details. It then 
#          exports these details into an organized Excel file with each script's data in a separate sheet.

import os
import json
import pandas as pd

def load_json(file_path):
    # DR: Load and parse a JSON file from the given file path
    with open(file_path, 'r') as file:
        return json.load(file)

def parse_script_data(json_data):
    # DR: Parses specific data from JSON concerning test automation scripts
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

def export_to_excel(scripts_data, output_file):
    # DR: Exports collected data into an Excel file, each script data in a separate sheet
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for script_name, actions in scripts_data.items():
            valid_sheet_name = script_name[:31].replace('/', '_').replace('\\', '_').replace('*', '_').replace('?', '_').replace(':', '_').replace('[', '_').replace(']', '_')
            df = pd.DataFrame(actions)
            df.to_excel(writer, sheet_name=valid_sheet_name, index=False)

def process_directory(directory):
    # DR: Process all JSON files in a specified directory
    scripts_data = {}
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            json_data = load_json(file_path)
            script_info, actions = parse_script_data(json_data)
            scripts_data[script_info['name']] = actions
    return scripts_data

if __name__ == '__main__':
    # DR: Main execution block to handle input and display results
    directory = input("Enter the directory containing JSON files: ")
    output_file = input("Enter the path for the output Excel file: ")
    scripts_data = process_directory(directory)
    export_to_excel(scripts_data, output_file)

    print(f"Processed JSON files have been exported to {output_file}")
