"""
File Comparison Script

Author: Duane Robinson
Date: 6/13/2024

Description:
This script compares two files to determine if they are identical and retrieves their creation dates.
It reads the files into DataFrames, compares the content, and prints the creation dates and whether
the files are identical.

Usage:
Update the 'file1_path' and 'file2_path' variables with the paths to the files you want to compare.
"""

import os
from datetime import datetime
import pandas as pd

# Function to get the creation date of a file
def get_creation_date(file_path):
    """
    Get the creation date of a file.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: Creation date of the file in 'YYYY-MM-DD HH:MM:SS' format.
    """
    creation_time = os.path.getctime(file_path)
    creation_date = datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')
    return creation_date

# Paths to the files
file1_path = "path/to/ORSISOUT20240612.txt"
file2_path = "path/to/ORSISOUT20240613_Pentaho_MA1.txt"

# Get creation dates
file1_creation_date = get_creation_date(file1_path)
file2_creation_date = get_creation_date(file2_path)

# Read the files into DataFrames
file1_df = pd.read_csv(file1_path, header=None, names=["ID"])
file2_df = pd.read_csv(file2_path, header=None, names=["ID"])

# Check if the files are identical
files_identical = file1_df.equals(file2_df)

# Print the results
print("File 1 Creation Date:", file1_creation_date)
print("File 2 Creation Date:", file2_creation_date)
print("Files Identical:", files_identical)
