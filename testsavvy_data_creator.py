# Excel Data Summary Exporter
# Date: April 21, 2024
# Developer: Duane Robinson
# Purpose: This script processes an Excel file to summarize data by counting occurrences of each value within specified fields.
#          It exports these summaries to a new Excel file, organizing each field's summary in separate sheets.
# IMPORTANT: This is the script that creates the TestSavvy_Data.xlsx file

import sys
import pandas as pd

def sanitize_sheet_name(name):
    # DR: Remove or replace invalid characters for Excel sheet names and truncate to the maximum length allowed by Excel.
    invalid_chars = '[]:*?/\\'
    for ch in invalid_chars:
        name = name.replace(ch, '_')  # Replace invalid characters with an underscore
    return name[:31]  # Excel sheet names have a max length of 31 characters

def process_excel(input_file):
    # DR: Load the spreadsheet and prepare dictionaries to store counts of important fields
    data = pd.read_excel(input_file)
    field_summary = {}

    # DR: Process each row in the DataFrame to count occurrences of each field value
    for index, row in data.iterrows():
        field_key = row['Field'].strip()
        field_value = str(row['Field Value']).strip()

        # Initialize the dictionary for each field key if not already present
        if field_key not in field_summary:
            field_summary[field_key] = {}

        # Count occurrences of each field value
        if field_value in field_summary[field_key]:
            field_summary[field_key][field_value] += 1
        else:
            field_summary[field_key][field_value] = 1

    # DR: Create new Excel writer to write the summary tab for each field
    with pd.ExcelWriter('output_summary_data.xlsx', engine='xlsxwriter') as writer:
        for key, value_counts in field_summary.items():
            summary_df = pd.DataFrame(list(value_counts.items()), columns=['Value', 'Count'])
            summary_df = summary_df.sort_values(by='Count', ascending=False)  # Sorting by count for better organization
            sanitized_sheet_name = sanitize_sheet_name(key)
            summary_df.to_excel(writer, sheet_name=sanitized_sheet_name, index=False)

if __name__ == "__main__":
    # DR: Main execution block to handle command line input and process the Excel file
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        process_excel(input_file)
    else:
        print("Please provide the Excel file path as an argument.")
