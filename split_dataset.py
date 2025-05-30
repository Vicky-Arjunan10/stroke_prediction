import os
import pandas as pd
import shutil

# Define the source and destination folders
source_folder = 'data'
destination_folder = 'raw_data'

# Ensure the destination folder exists
os.makedirs(destination_folder, exist_ok=True)

# Clear the raw_data folder before splitting
for file in os.listdir(destination_folder):
    file_path = os.path.join(destination_folder, file)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)  # Remove file or symbolic link
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)  # Remove directory
    except Exception as e:
        print(f'Failed to delete {file_path}. Reason: {e}')

# Load the CSV file (raw_data.csv) from the data folder
input_file = os.path.join(source_folder, 'raw_data.csv')
data = pd.read_csv(input_file)

# Get the total number of rows in the data
total_rows = len(data)

# Specify the number of files you want to generate
num_files = int(input("Enter the number of files to generate: "))

# Calculate the number of rows per file based on the specified number of files
rows_per_file = total_rows // num_files + (1 if total_rows % num_files else 0)

# Split and save into the specified number of files in the raw_data folder
for i in range(0, total_rows, rows_per_file):
    # Extract the chunk of data for each file
    chunk = data[i:i + rows_per_file]

    # Generate the output file name
    output_file = os.path.join(destination_folder, f'output_{i // rows_per_file + 1}.csv')

    # Save the chunk to a new CSV file
    chunk.to_csv(output_file, index=False)

    print(f'Saved {output_file}')
