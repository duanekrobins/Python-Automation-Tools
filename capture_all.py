"""
This Python script processes a JSON file and outputs its contents to an Excel spreadsheet.
It specifically extracts data from nested structures under 'sequenceList', each containing
a 'scenarioFlowList'. The script extracts specific properties from each 'scenarioFlowList'
and compiles them into an Excel file. This helps in organizing and analyzing data from
complex JSON structures in a more accessible format.

Developer: Duane Robinson
Date: April 25th, 2024
"""

import json
import pandas as pd

def extract_data(input_file, output_file):
    # Load the JSON data from the file
    with open(input_file, 'r') as file:
        data = json.load(file)
    
    # Retrieve the list of sequences, assuming it's directly under the root of the JSON structure
    sequence_list = data.get('sequenceList', [])

    # Initialize a list to hold data extracted from each scenario flow
    extracted_data = []

    # Process each sequence in the sequenceList
    for sequence in sequence_list:
        # Process each scenario flow within the current sequence
        for scenario in sequence.get('scenarioFlowList', []):
            # Extract specified properties from the scenario flow and store them in a dictionary
            extracted_info = {
                'action_classification': scenario.get('action_classification', ''),
                'action_code': scenario.get('action_code', ''),
                'action_id': scenario.get('action_id', ''),
                'name': scenario.get('name', ''),
                'interface_element_id': scenario.get('interface_element_id', ''),
                'action_name': scenario.get('action_name', '')
            }
            # Append the dictionary to the list of extracted data
            extracted_data.append(extracted_info)

    # Convert the list of extracted data into a DataFrame for better structure and to prepare for output
    df = pd.DataFrame(extracted_data)

    # Output the DataFrame to an Excel file, not including the DataFrame index
    df.to_excel(output_file, index=False)

def main():
    # Prompt user for input and output file names
    input_file = input("Enter the input JSON file name: ")
    output_file = input("Enter the output Excel file name: ")

    # Extract data from the input file and save it to the specified output file
    extract_data(input_file, output_file)
    print(f"Data has been successfully extracted and saved to {output_file}")

if __name__ == "__main__":
    main()
