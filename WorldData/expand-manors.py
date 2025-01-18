import os
import json
import random

def modify_home_wealthy_files(directory):
    print(f"Scanning directory: {directory}")
    files_found = 0
    files_updated = 0

    for filename in os.listdir(directory):
        print(f"Checking file: {filename}")
        if filename.startswith("location") and filename.endswith(".json"):
            files_found += 1
            filepath = os.path.join(directory, filename)

            try:
                # Load the JSON file
                with open(filepath, 'r') as file:
                    data = json.load(file)

                # Check if LocationType is HomeWealthy
                if data.get("MapTableData", {}).get("LocationType") != "HomeWealthy":
                    print(f"Skipping file (not HomeWealthy): {filename}")
                    continue

                # Randomly choose Height and Width
                height, width = random.choice([(2, 3), (3, 2), (3, 3)])
                data["Exterior"]["ExteriorData"]["Height"] = height
                data["Exterior"]["ExteriorData"]["Width"] = width

                # Determine ClimateType and block prefixes
                climate_type = data.get("Climate", {}).get("ClimateType", "")
                block_prefix = "FARMBA" if climate_type.lower() == "desert" else "FARMAA"

                # Generate new BlockNames
                block_count = height * width
                existing_blocks = data["Exterior"]["ExteriorData"].get("BlockNames", [])

                if len(existing_blocks) == 0:
                    print(f"No existing blocks found in {filename}, skipping.")
                    continue

                # Keep the original block
                original_block = existing_blocks[0]
                used_blocks = set()
                new_blocks = []

                # Generate blocks with 75% chance from 10-13 and 25% from 00-09 (excluding certain blocks)
                while len(new_blocks) < block_count - 1:
                    block_type = random.choices(["10-13", "00-09"], weights=[75, 25])[0]
                    if block_type == "10-13":
                        new_blocks.append(f"{block_prefix}{random.randint(10, 13)}.RMB")
                    else:
                        while True:
                            candidate = random.randint(0, 9)
                            if candidate not in {4, 5, 7} and f"{block_prefix}{candidate:02d}.RMB" not in used_blocks:
                                block = f"{block_prefix}{candidate:02d}.RMB"
                                new_blocks.append(block)
                                used_blocks.add(block)
                                break

                # Determine central position for the original block
                if (width, height) == (3, 2):
                    central_position = random.choice([1, 4])
                elif (width, height) == (2, 3):
                    central_position = random.choice([2, 3])
                else:  # 3x3
                    central_position = 4

                # Insert the original block at the central position
                new_blocks.insert(central_position, original_block)

                # Update BlockNames
                data["Exterior"]["ExteriorData"]["BlockNames"] = new_blocks

                # Save the modified JSON file
                with open(filepath, 'w') as file:
                    json.dump(data, file, indent=4)

                print(f"Updated: {filename}")
                files_updated += 1

            except Exception as e:
                print(f"Error processing file {filename}: {e}")

    print(f"Total files found: {files_found}")
    print(f"Total files updated: {files_updated}")

# Replace '.' with the directory containing the location*.json files
modify_home_wealthy_files(".")

