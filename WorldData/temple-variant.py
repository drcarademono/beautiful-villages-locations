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
    os.makedirs(target_directory, exist_ok=True)
    json_files = glob.glob(os.path.join(source_directory, '*.json'))

    tempasa0_blocks = {}
    total_count = 0

    for file in json_files:
        with open(file, 'r') as json_file:
            data = json.load(json_file)
        block_names = find_block_names(data)
        if block_names:
            tempasa0_indices = [i for i, name in enumerate(block_names) if name.startswith("TEMPASA0")]
            if tempasa0_indices:
                tempasa0_blocks[file] = tempasa0_indices
                total_count += len(tempasa0_indices)

    modification_pool = []
    for i in range(3):  # For numbers 0 to 2
        modification_pool.extend([i] * (total_count // 3))

    for i in random.sample(range(3), total_count % 3):
        modification_pool.append(i)

    random.shuffle(modification_pool)

    current_index = 0
    for file, indices in tempasa0_blocks.items():
        modified = False
        with open(file, 'r') as json_file:
            data = json.load(json_file)

        block_names = find_block_names(data)
        if block_names:
            for i in indices:
                new_number = modification_pool[current_index]
                block_name = block_names[i]
                # Adjusted to preserve the suffix ".RMB"
                new_block_name = "TEMPASA" + str(new_number) + block_name[block_name.index("TEMPASA0") + 8:]
                block_names[i] = new_block_name
                modified = True
                current_index += 1

        if modified:
            filename = os.path.basename(file)
            with open(os.path.join(target_directory, filename), 'w') as outfile:
                json.dump(data, outfile, indent=4)

    print(f"Total TEMPASA0 blocks modified: {total_count}")
    print("Modifications distribution:", {i: modification_pool.count(i) for i in range(3)})

# Usage
current_directory = '.'  # Current directory
target_directory = '.'  # Target directory
modify_json_files(current_directory, target_directory)

