# JSON to Excel Data Exporter for Test Automation Scripts
# Date: April 21, 2024
# Developer: Duane Robinson
# Purpose: This script processes directories of JSON files by extracting specific automation 
#          test data and exporting it to an Excel file. It is specifically designed to parse
#          test scripts for relevant details like script names, descriptions, and step associations.

import os
import json
import pandas as pd

def load_json(file_path):
    # DR: Load and parse a JSON file from the given file path
    with open(file_path, 'r') as file:
        return json.load(file)

def parse_script_data(json_data, script_name):
    # DR: Extracts specific details from JSON data for each test automation script
    actions = []
    for sequence in json_data.get('sequenceList', []):
        for scenario in sequence.get('scenarioFlowList', []):
            if 'stepAssociation' in scenario and scenario['stepAssociation'] is not None:
                step_association_value = scenario['stepAssociation'].get('value', None)
                if step_association_value:
                    actions.append({
                        'Script Name': script_name,
                        'Name': scenario.get('name', 'No name'),
                        'English_Text': scenario.get('english_text', 'No English text'),
                        'Step_Association_Value': step_association_value
                    })
    return actions

def process_directory(directory):
    # DR: Process all JSON files within the specified directory and compile data
    all_data = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            script_name = filename.split("27_")[-1].replace('.json', '')
            file_path = os.path.join(directory, filename)
            json_data = load_json(file_path)
            script_data = parse_script_data(json_data, script_name)
            all_data.extend(script_data)
    return all_data

def export_to_excel(data, output_file):
    # DR: Exports the processed data into an Excel file
    df = pd.DataFrame(data)
    df.to_excel(output_file, index=False)

if __name__ == '__main__':
    # DR: Main execution block to handle user input and display results
    directory = input("Enter the directory containing JSON files: ")
    output_file = input("Enter the path for the output Excel file: ")
    all_data = process_directory(directory)
    export_to_excel(all_data, output_file)
    print(f"Processed JSON files have been exported to {output_file}")
