"""
Python Script to Analyze Directories and Output File Statistics to Excel

Author: Duane K Robinson
Date: 2024-06-24

This script performs the following tasks:
1. Prompts for a directory path to parse or uses the current directory if none is provided.
2. Ensures the specified directory exists.
3. Retrieves all files in the directory and its subdirectories using efficient directory traversal.
4. Calculates file statistics including total number of files, total file size, and splits these by the fiscal year 2013 cutoff.
5. Outputs the directory statistics into an Excel spreadsheet and provides a grand total at the end.
"""

import os
from datetime import datetime
from openpyxl import Workbook
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
    """Analyze file statistics in the directory."""
    total_files = 0
    total_size = 0
    files_before_fy = 0
    size_before_fy = 0
    files_after_fy = 0
    size_after_fy = 0

    for entry in scan_files(directory):
        total_files += 1
        file_size = stat(entry.path).st_size
        total_size += file_size
        file_mod_time = datetime.fromtimestamp(stat(entry.path).st_mtime)
        if file_mod_time < fy_cutoff:
            files_before_fy += 1
            size_before_fy += file_size
        else:
            files_after_fy += 1
            size_after_fy += file_size

    return {
        'directory': directory,
        'total_files': total_files,
        'total_size': total_size,
        'files_before_fy': files_before_fy,
        'size_before_fy': size_before_fy,
        'files_after_fy': files_after_fy,
        'size_after_fy': size_after_fy
    }

def format_size(size):
    """Convert size to a readable format (bytes, KB, MB, GB)."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

def main():
    # Prompt user for directory path or use the current directory
    directory_input = input("Enter the directory to parse (press enter to use current directory): ")
    directory_to_scan = directory_input if directory_input else os.getcwd()

    if not os.path.exists(directory_to_scan):
        print("The specified directory does not exist.")
        return

    # Prompt for output file location and name
    output_file = input("Enter the full path and file name for the output Excel file: ")

    # Validate the output file path
    if not output_file.endswith('.xlsx'):
        output_file = os.path.join(output_file, 'DirectoryAnalysis.xlsx')

    directories = []
    with ThreadPoolExecutor() as executor:
        results = executor.map(analyze_directory, [d.path for d in scandir(directory_to_scan) if d.is_dir()])
        directories = list(results)

    if not directories:
        print("No directories found.")
        return

    # Create the workbook and sheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Directory Analysis"

    # Write headers
    headers = ["Directory", "Total Files", "Files Before FY 2013", "Files After FY 2013",
               "Total Size", "Size Before FY 2013", "Size After FY 2013"]
    ws.append(headers)

    # Initialize grand totals
    grand_total_files = 0
    grand_files_before_fy = 0
    grand_files_after_fy = 0
    grand_total_size = 0
    grand_size_before_fy = 0
    grand_size_after_fy = 0

    # Write directory statistics
    for dir_stats in directories:
        grand_total_files += dir_stats['total_files']
        grand_files_before_fy += dir_stats['files_before_fy']
        grand_files_after_fy += dir_stats['files_after_fy']
        grand_total_size += dir_stats['total_size']
        grand_size_before_fy += dir_stats['size_before_fy']
        grand_size_after_fy += dir_stats['size_after_fy']
        
        ws.append([
            dir_stats['directory'],
            dir_stats['total_files'],
            dir_stats['files_before_fy'],
            dir_stats['files_after_fy'],
            format_size(dir_stats['total_size']),
            format_size(dir_stats['size_before_fy']),
            format_size(dir_stats['size_after_fy'])
        ])

    # Write grand totals
    ws.append([
        "Grand Total",
        grand_total_files,
        grand_files_before_fy,
        grand_files_after_fy,
        format_size(grand_total_size),
        format_size(grand_size_before_fy),
        format_size(grand_size_after_fy)
    ])

    # Save the workbook
    wb.save(output_file)
    print(f"Directory analysis has been saved to {output_file}")

if __name__ == "__main__":
    main()

