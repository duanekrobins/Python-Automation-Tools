# Test Script Data to Excel Exporter with Tables
# Date: April 21, 2024
# Developer: Duane Robinson
# Purpose: This script processes directories of JSON files related to test automation, extracting key details about test scripts,
#          and exports these details to an Excel file with data organized in tables for better readability and analysis.

import os
import json
import pandas as pd
import openpyxl

def load_json(file_path):
    # DR: Load and parse a JSON file from the given file path
    with open(file_path, 'r') as file:
        return json.load(file)

def parse_script_data(json_data):
    # DR: Extracts detailed script information from JSON data, including name, description, and actions
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
    # DR: Exports script data into Excel, organizing each script's actions into separate tables within sheets
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        sheet_name_count = {}  # Track duplicate sheet names
        table_name_count = {}  # Track duplicate table names
        for script_name, actions in scripts_data.items():
            base_sheet_name = script_name[:31].replace('/', '_').replace('\\\\', '_').replace('*', '_').replace('?', '_').replace(':', '_').replace('[', '_').replace(']', '_').replace(' ', '_')
            # Ensure each sheet name is unique by appending numbers if necessary
            sheet_count = sheet_name_count.get(base_sheet_name, 0)
            valid_sheet_name = f"{base_sheet_name}_{sheet_count}" if sheet_count > 0 else base_sheet_name
            sheet_name_count[base_sheet_name] = sheet_count + 1
            df = pd.DataFrame(actions)
            df.to_excel(writer, sheet_name=valid_sheet_name, index=False)

def process_directory(directory):
    # DR: Process all JSON files in a specified directory, compiling data for export
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
