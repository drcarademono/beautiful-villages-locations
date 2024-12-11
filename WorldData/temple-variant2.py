import os
import json
import random

def modify_tempas_elements(block_names):
    """Randomly modify TEMPASD0 and TEMPASF0 elements to TEMPASD1 and TEMPASF1 with 50% probability."""
    for idx, block_name in enumerate(block_names):
        if block_name == "TEMPASD0.RMB" and random.random() < 0.5:
            block_names[idx] = "TEMPASD1.RMB"
        elif block_name == "TEMPASF0.RMB" and random.random() < 0.5:
            block_names[idx] = "TEMPASF1.RMB"

def process_json_file(filepath):
    """Process a single RMB.json file."""
    with open(filepath, 'r') as file:
        data = json.load(file)
    
    # Only process files where LocationType is NOT TownHamlet
    if data.get("MapTableData", {}).get("LocationType") != "TownHamlet":
        exterior_data = data.get("Exterior", {}).get("ExteriorData", {})
        block_names = exterior_data.get("BlockNames", [])
        
        if block_names:
            modify_tempas_elements(block_names)
            # Update the data
            exterior_data["BlockNames"] = block_names
        
        # Write back the modified file
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)

def main():
    """Main function to iterate over all RMB.json files in the directory."""
    for filename in os.listdir("."):
        if filename.endswith(".json"):
            print(f"Processing {filename}...")
            process_json_file(filename)
    print("Processing complete.")

if __name__ == "__main__":
    main()

