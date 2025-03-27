import os
import json
import re

def replace_tempba_with_tempbs(block_names):
    """Replace all TEMPBA**.RMB blocks with TEMPBS**.RMB."""
    for idx, block_name in enumerate(block_names):
        match = re.match(r"^TEMPBA(.+)\.RMB$", block_name)
        if match:
            suffix = match.group(1)
            block_names[idx] = f"TEMPBS{suffix}.RMB"

def process_json_file(filepath):
    """Process a single RMB.json file."""
    with open(filepath, 'r') as file:
        data = json.load(file)

    # Skip TownHamlet locations
    if data.get("MapTableData", {}).get("LocationType") != "TownHamlet":
        exterior_data = data.get("Exterior", {}).get("ExteriorData", {})
        block_names = exterior_data.get("BlockNames", [])

        if block_names:
            replace_tempba_with_tempbs(block_names)
            exterior_data["BlockNames"] = block_names  # Update in place

        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)

def main():
    """Iterate over all .json files in the current directory."""
    for filename in os.listdir("."):
        if filename.endswith(".json"):
            print(f"Processing {filename}...")
            process_json_file(filename)
    print("Processing complete.")

if __name__ == "__main__":
    main()

