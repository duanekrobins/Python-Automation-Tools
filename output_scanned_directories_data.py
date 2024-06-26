"""
Python Script to Analyze Directories and Output File Statistics to Excel

Author: Duane K Robinson
Date: 2024-06-25

This script performs the following tasks:
1. Prompts for a directory path to parse or uses the current directory if none is provided.
2. Ensures the specified directory exists.
3. Retrieves all files in the directory and its subdirectories using efficient directory traversal.
4. Calculates file statistics including total number of files, total file size, and splits these by the fiscal year 2013 cutoff.
5. Outputs the directory statistics into an Excel spreadsheet and provides a grand total at the end.
6. Writes the directory statistics to a MySQL database.
7. Allows pausing the script using Ctrl+Z.
8. Clears all records in the database table before writing new data.
"""

import os
import time
import mysql.connector
from datetime import datetime
from openpyxl import Workbook
from concurrent.futures import ThreadPoolExecutor, as_completed
from os import scandir, stat
from tqdm import tqdm
import keyboard

# Fiscal year cutoff for 2013 starts in July
fy_cutoff = datetime(2012, 7, 1)

# Database connection details
db_config = {
    'user': '',
    'password': '',
    'host': '127.0.0.1',
    'database': 'delete_week'
}

# Global pause flag
paused = False

def handle_pause():
    global paused
    paused = not paused
    if paused:
        print("Script paused. Press Ctrl+Z to resume.")
    else:
        print("Script resumed.")

# Set the keyboard listener for Ctrl+Z
keyboard.add_hotkey('ctrl+z', handle_pause)

def scan_files(directory):
    """Scan the directory using scandir for improved performance."""
    with scandir(directory) as entries:
        for entry in entries:
            if entry.is_dir(follow_symlinks=False):
                # Recursively scan subdirectories.
                yield from scan_files(entry.path)
            elif entry.is_file(follow_symlinks=False):
                # Yield file entries.
                yield entry

def count_directories_and_files(directory):
    """Count total directories and files."""
    total_directories = 0
    total_files = 0
    with scandir(directory) as entries:
        for entry in entries:
            if entry.is_dir(follow_symlinks=False):
                total_directories += 1
                # Recursively count files and directories in subdirectories.
                subdir_files, subdir_dirs = count_directories_and_files(entry.path)
                total_files += subdir_files
                total_directories += subdir_dirs
            elif entry.is_file(follow_symlinks=False):
                total_files += 1
    return total_files, total_directories

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

def clear_database():
    """Clear all records in the database table."""
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("TRUNCATE TABLE output_directory_scan_data")
    connection.commit()
    cursor.close()
    connection.close()

def save_to_database(data):
    """Save directory analysis data to the MySQL database."""
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    
    insert_query = """
    INSERT INTO output_directory_scan_data 
    (Directory, total_files, files_before_end_date, files_after_end_date, total_size_of_files_before_ed, total_size_of_files_after_ed) 
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    cursor.execute(insert_query, (
        data['directory'],
        data['total_files'],
        data['files_before_fy'],
        data['files_after_fy'],
        str(data['size_before_fy']),
        str(data['size_after_fy'])
    ))
    
    connection.commit()
    cursor.close()
    connection.close()

def main():
    try:
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

        # Clear the database table before writing new data
        clear_database()

        # Count total directories and files
        print("Counting total directories and files...")
        total_files, total_directories = count_directories_and_files(directory_to_scan)
        print(f"Total directories: {total_directories}, Total files: {total_files}")

        # Initialize the workbook and sheet
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

        # Analyze directories with a progress bar
        directories = [directory_to_scan]
        for root, dirs, files in os.walk(directory_to_scan):
            for d in dirs:
                directories.append(os.path.join(root, d))

        # Set maximum number of threads to reduce memory usage
        max_workers = min(32, len(directories))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_directory = {executor.submit(analyze_directory, d): d for d in directories}
            for future in tqdm(as_completed(future_to_directory), total=len(directories), desc="Analyzing directories"):
                while paused:
                    time.sleep(1)
                try:
                    directory_analysis = future.result()
                    if directory_analysis:
                        dir_stats = directory_analysis
                        
                        # Print the current directory being analyzed
                        print(f"Currently analyzing: {dir_stats['directory']}")

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
                        
                        # Save to database
                        save_to_database(dir_stats)
                        
                except Exception as e:
                    print(f"Error analyzing directory {future_to_directory[future]}: {e}")

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

    except KeyboardInterrupt:
        print("Process interrupted by user. Exiting...")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()

