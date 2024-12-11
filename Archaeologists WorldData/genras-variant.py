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

    # Step 1: Collect all GENRAS blocks
    all_genras_blocks = {}
    for file in json_files:
        with open(file, 'r') as json_file:
            data = json.load(json_file)
        block_names = find_block_names(data)
        if block_names:
            for block_name in block_names:
                if block_name.startswith("GENRAS") and block_name[6:8] in ["00", "01", "02"]:
                    all_genras_blocks.setdefault(file, []).append(block_name)

    # Step 2: Randomly select half of these blocks to be modified
    total_genras_blocks = sum(len(blocks) for blocks in all_genras_blocks.values())
    num_blocks_to_modify = total_genras_blocks // 2
    blocks_to_modify = set()
    while len(blocks_to_modify) < num_blocks_to_modify:
        file = random.choice(list(all_genras_blocks.keys()))
        if all_genras_blocks[file]:
            block_name = random.choice(all_genras_blocks[file])
            blocks_to_modify.add((file, block_name))

    # Step 3: Iterate over the files again and apply the modifications
    for file in json_files:
        modified = False
        with open(file, 'r') as json_file:
            data = json.load(json_file)

        block_names = find_block_names(data)
        if block_names:
            for i, block_name in enumerate(block_names):
                if (file, block_name) in blocks_to_modify:
                    # Extract the suffix, add three, and reconstruct the block name
                    suffix = int(block_name[6:8]) + 3
                    modified_name = "GENRAS" + f"{suffix:02d}" + block_name[8:]
                    block_names[i] = modified_name
                    modified = True

        if modified:
            # Save the modified JSON to the target directory
            filename = os.path.basename(file)
            with open(os.path.join(target_directory, filename), 'w') as outfile:
                json.dump(data, outfile, indent=4)

# Usage
current_directory = '.'  # Current directory
target_directory = '.'  # Target directory
modify_json_files(current_directory, target_directory)

