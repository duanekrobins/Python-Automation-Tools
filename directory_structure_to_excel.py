"""
Python Script to Filter Files by Creation Date and Output to Excel

Author: Duane K Robinson
Date: 2024-06-24

This script performs the following tasks:
1. Defines the directory path and date range for filtering files.
2. Ensures the specified directory exists.
3. Retrieves all files in the parent directory and its subdirectories.
4. Filters the files based on their creation date within the specified range.
5. Outputs the filtered files along with their directory paths into an Excel spreadsheet, 
   mimicking the hierarchical structure observed in the provided example spreadsheet.
"""

import os
import pandas as pd
from datetime import datetime
from openpyxl import Workbook

# Define the directory path
parent_directory_path = r"Y:\QualityAssurance"

# Define the date range
start_date = datetime(2013, 1, 1)
end_date = datetime.now()

# Ensure the directory exists
if not os.path.exists(parent_directory_path):
    print("The specified parent directory does not exist.")
else:
    # Get all files in the parent directory and its subdirectories
    files = []
    for root, dirs, file_names in os.walk(parent_directory_path):
        for file_name in file_names:
            file_path = os.path.join(root, file_name)
            file_info = os.stat(file_path)
            files.append({
                'file_path': file_path,
                'creation_time': datetime.fromtimestamp(file_info.st_ctime),
                'last_access_time': datetime.fromtimestamp(file_info.st_atime),
                'directory_name': root,
                'file_name': file_name
            })

    # Filter files by creation date range
    filtered_files = [
        file for file in files 
        if start_date <= file['creation_time'] <= end_date
    ]

    # Sort filtered files by directory name
    filtered_files.sort(key=lambda x: x['directory_name'])

    # Create a DataFrame for the filtered files
    df_filtered_files = pd.DataFrame(filtered_files)

    # Prepare the structure similar to the provided spreadsheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Filtered Files"

    # Add header
    headers = ['File', 'Directory', 'Created']
    ws.append(headers)

    # Add data rows
    for file in filtered_files:
        ws.append([file['file_name'], file['directory_name'], file['creation_time']])

    # Save the workbook
    output_path = '/dev/python/Filtered_Files.xlsx'
    wb.save(output_path)
    print(f"Filtered files information has been saved to {output_path}")
