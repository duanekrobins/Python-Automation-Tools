"""
Python Script to Filter Directories by File Modification Dates and Output to Excel

Author: Duane K Robinson
Date: 2024-06-24

This script performs the following tasks:
1. Prompts for a directory path to parse or uses the current directory if none is provided.
2. Ensures the specified directory exists.
3. Retrieves all files in the directory and its subdirectories using efficient directory traversal.
4. Analyzes the last modified dates of the files to determine the directory color coding based on fiscal year cutoff.
5. Outputs the directory names into an Excel spreadsheet with color coding.
"""

import os
from datetime import datetime
from openpyxl import Workbook, styles
from concurrent.futures import ThreadPoolExecutor
from os import scandir, stat

# Fiscal year cutoff for 2013 starts in July
fy_cutoff = datetime(2012, 7, 1)

def scan_files(directory):
    """Scan the directory using scandir for improved performance."""
    with scandir(directory) as entries:
        for entry in entries:
            if entry.is_dir(follow_symlinks=False):
                yield from scan_files(entry.path)
            elif entry.is_file(follow_symlinks=False):
                yield entry

def analyze_directory(directory):
    """Analyze file modification dates in the directory."""
    all_before_fy = True
    any_before_fy = False
    all_after_fy = True

    for entry in scandir(directory):
        if entry.is_file(follow_symlinks=False):
            file_mod_time = datetime.fromtimestamp(stat(entry.path).st_mtime)
            if file_mod_time < fy_cutoff:
                any_before_fy = True
                all_after_fy = False
            else:
                all_before_fy = False

    if all_before_fy:
        return (directory, 'red')
    elif any_before_fy:
        return (directory, 'purple')
    elif all_after_fy:
        return (directory, 'blue')
    return None

def main():
    # Prompt user for directory path or use the current directory
    directory_input = input("Enter the directory to parse (press enter to use current directory): ")
    directory_to_scan = directory_input if directory_input else os.getcwd()

    if not os.path.exists(directory_to_scan):
        print("The specified directory does not exist.")
        return

    # Prompt for output file location and name
    output_file = input("Enter the full path and file name for the output Excel file: ")

    directories = []
    with ThreadPoolExecutor() as executor:
        results = executor.map(analyze_directory, [d.path for d in scandir(directory_to_scan) if d.is_dir()])
        directories = [result for result in results if result]

    if not directories:
        print("No directories matched the criteria.")
        return

    # Create the workbook and sheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Directory Analysis"

    # Write headers
    ws.append(["Directory Name", "Status"])

    # Write directory names with colors
    for directory, color in directories:
        cell = ws.append([directory])[0][0]
        cell.font = styles.Font(color=color)

    # Save the workbook
    wb.save(output_file)
    print(f"Directory analysis has been saved to {output_file}")

if __name__ == "__main__":
    main()
