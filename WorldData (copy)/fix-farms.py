import json
import os
import glob
import random

def find_block_names(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'BlockNames' and isinstance(value, list):
                return value
            elif isinstance(value, (dict, list)):
                result = find_block_names(value)
                if result is not None:
                    return result
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                result = find_block_names(item)
                if result is not None:
                    return result
    return None

def modify_json_files(source_directory, target_directory):
    # Create the target directory if it doesn't exist
    os.makedirs(target_directory, exist_ok=True)

    # List all JSON files in the source directory
    json_files = glob.glob(os.path.join(source_directory, '*.json'))

    for file in json_files:
        try:
            # Read the JSON file
            with open(file, 'r') as json_file:
                data = json.load(json_file)

            # Find and modify the BlockNames
            block_names = find_block_names(data)
            if block_names:
                for i, block_name in enumerate(block_names):
                    # Check if the block name is exactly 'FARMAA' without any suffix
                    if block_name == "FARMAA":
                        # Generate a random suffix from 00.RMB to 09.RMB
                        suffix = f"{random.randint(0, 9):02d}.RMB"
                        modified_name = block_name + suffix
                        block_names[i] = modified_name

            # Save the modified JSON to the target directory
            filename = os.path.basename(file)
            with open(os.path.join(target_directory, filename), 'w') as outfile:
                json.dump(data, outfile, indent=4)

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON in file {file}: {e}")
        except IOError as e:
            print(f"Error processing file {file}: {e}")

# Usage
current_directory = '.'  # Current directory
target_directory = '.'  # Target directory (the 'farms' folder)
modify_json_files(current_directory, target_directory)

