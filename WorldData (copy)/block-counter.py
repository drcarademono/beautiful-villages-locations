import os
import json
import csv
from collections import Counter

def count_block_names_in_json(folder_path='.'):
    block_name_counter = Counter()

    # List all files in the current folder
    for file in os.listdir(folder_path):
        if file.endswith('.json'):
            file_path = os.path.join(folder_path, file)

            # Open and read the JSON file
            with open(file_path, 'r') as json_file:
                try:
                    data = json.load(json_file)

                    # Extract BlockNames list and update the counter
                    block_names = data.get('Exterior', {}).get('ExteriorData', {}).get('BlockNames', [])
                    block_name_counter.update(block_names)
                except json.JSONDecodeError:
                    print(f"Error reading JSON file: {file_path}")

    return block_name_counter

# Execute the function and get the results
block_name_counts = count_block_names_in_json()

# Write the results to a CSV file
with open('block-counts.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Block Name', 'Count'])  # Writing the header

    for block_name, count in block_name_counts.items():
        writer.writerow([block_name, count])

print("Block counts have been written to block-counts.csv")

