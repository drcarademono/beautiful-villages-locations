import os
import random

def update_position_in_file(file_path, unique_positions, used_positions):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Simple find-and-replace for '"Position": 0'
    occurrences = content.count('"Position": 0')
    for _ in range(occurrences):
        if unique_positions:
            new_position = unique_positions.pop()
            used_positions.add(new_position)
            content = content.replace('"Position": 0', f'"Position": {new_position}', 1)
        else:
            print(f"Ran out of unique positions while processing {file_path}")
            break

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def process_all_json_files(directory):
    unique_positions = list(range(5000, 10001))  # Example range
    random.shuffle(unique_positions)  # Shuffle to ensure uniqueness across files
    used_positions = set()  # Track used positions to avoid duplicates

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            update_position_in_file(file_path, unique_positions, used_positions)

# Process all JSON files in the current directory
process_all_json_files('.')

