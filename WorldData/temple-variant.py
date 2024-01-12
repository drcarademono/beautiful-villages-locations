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

    # Collect all TEMPASH0 blocks
    tempash0_blocks = {}  # file -> list of block indices
    total_count = 0

    for file in json_files:
        with open(file, 'r') as json_file:
            data = json.load(json_file)
        block_names = find_block_names(data)
        if block_names:
            tempash0_indices = [i for i, name in enumerate(block_names) if name.startswith("TEMPASH0")]
            if tempash0_indices:
                tempash0_blocks[file] = tempash0_indices
                total_count += len(tempash0_indices)

    # Create a pool of numbers (0-4) for equal distribution
    modification_pool = []
    for i in range(5):
        modification_pool.extend([i] * (total_count // 5))

    # If there's a remainder, randomly add the extra numbers
    for i in random.sample(range(5), total_count % 5):
        modification_pool.append(i)

    random.shuffle(modification_pool)  # Shuffle to randomize the distribution

    # Apply modifications
    current_index = 0
    for file, indices in tempash0_blocks.items():
        modified = False
        with open(file, 'r') as json_file:
            data = json.load(json_file)

        block_names = find_block_names(data)
        if block_names:
            for i in indices:
                new_number = modification_pool[current_index]
                block_name = block_names[i]
                block_names[i] = block_name[:-5] + str(new_number) + block_name[-4:]
                modified = True
                current_index += 1

        if modified:
            # Save the modified JSON to the target directory
            filename = os.path.basename(file)
            with open(os.path.join(target_directory, filename), 'w') as outfile:
                json.dump(data, outfile, indent=4)

    print(f"Total TEMPASH0 blocks modified: {total_count}")
    print("Modifications distribution:", {i: modification_pool.count(i) for i in range(5)})



# Usage
current_directory = '.'  # Current directory
target_directory = '.'  # Target directory
modify_json_files(current_directory, target_directory)

