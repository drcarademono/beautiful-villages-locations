import os
import json
import random

def modify_location_files(directory):
    print(f"Scanning directory: {directory}")
    files_found = 0
    files_updated = 0

    for filename in os.listdir(directory):
        # Debug: Log the filename being checked
        print(f"Checking file: {filename}")
        if filename.startswith("location") and filename.endswith(".json"):
            files_found += 1
            filepath = os.path.join(directory, filename)

            try:
                # Load the JSON file
                with open(filepath, 'r') as file:
                    data = json.load(file)

                # Check if LocationType is HomeFarms
                if data.get("MapTableData", {}).get("LocationType") != "HomeFarms":
                    print(f"Skipping file (not HomeFarms): {filename}")
                    continue

                # Randomly choose Height and Width
                height, width = random.choice([(1, 2), (2, 1), (2, 2)])
                data["Exterior"]["ExteriorData"]["Height"] = height
                data["Exterior"]["ExteriorData"]["Width"] = width

                # Determine ClimateType and choose appropriate block names
                climate_type = data.get("Climate", {}).get("ClimateType", "")
                block_prefix = "FARMBA" if climate_type.lower() == "desert" else "FARMAA"

                # Generate new BlockNames
                block_count = height * width
                existing_blocks = data["Exterior"]["ExteriorData"].get("BlockNames", [])
                new_blocks_needed = block_count - len(existing_blocks)

                # Generate new block names as needed
                new_blocks = [f"{block_prefix}{random.randint(10, 13)}.RMB" for _ in range(new_blocks_needed)]

                # Combine and shuffle existing and new blocks
                combined_blocks = existing_blocks + new_blocks
                random.shuffle(combined_blocks)

                # Update BlockNames
                data["Exterior"]["ExteriorData"]["BlockNames"] = combined_blocks

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
modify_location_files(".")

