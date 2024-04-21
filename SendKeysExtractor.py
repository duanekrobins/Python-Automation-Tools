# Comprehensive JSON Parser for Test Automation
# Date: April 21, 2024
# Developer: Duane Robinson
# Purpose: This script parses .json files containing test automation data, specifically extracting 
#          information related to web interaction commands like send_keys. It structures this data 
#          for further processing or reporting.

import json
import re

def load_json(file_path):
    # DR: Load and parse a JSON file from the given file path
    with open(file_path, 'r') as file:
        return json.load(file)

def extract_send_keys_data(json_data):
    # DR: Extracts data related to send_keys commands from the JSON data
    entries = []
    # DR: Regular expression to match the send_keys command and extract the XPath and data
    pattern = re.compile(r'find_element_by_xpath\\("([^"]+)"\\)\\.send_keys\\(([^)]+)\\)')
    
    for sequence in json_data.get('sequenceList', []):
        for scenario in sequence.get('scenarioFlowList', []):
            for action in scenario.get('scenarioFlowReuseList', []):
                action_code = action.get('action_code', '')
                if action_code:
                    matches = pattern.findall(action_code)
                    for xpath, data in matches:
                        # DR: Clean up the data string if it's a direct string input
                        data_cleaned = data.strip('"').replace('Keys.CONTROL+"a"+Keys.DELETE', '').strip('+').strip('"')
                        entry = {"XPath": xpath, "Data": data_cleaned}
                        entries.append(entry)

    return entries

if __name__ == '__main__':
    # DR: Main execution block to handle input and display results
    file_path = input("Enter the path to your JSON file: ")
    json_data = load_json(file_path)
    send_keys_data = extract_send_keys_data(json_data)
    print(json.dumps(send_keys_data, indent=4))
