import os
import json
import random

def modify_genras_elements(block_names):
    """Randomly modify half of GENRAS00, GENRAS01, GENRAS02 to GENRAS03, GENRAS04, GENRAS05."""
    target_elements = ["GENRAS00.RMB", "GENRAS01.RMB", "GENRAS02.RMB"]
    replacement_options = ["GENRAS03.RMB", "GENRAS04.RMB", "GENRAS05.RMB"]
    
    # Find indices of elements to modify
    indices_to_modify = [idx for idx, block_name in enumerate(block_names) if block_name in target_elements]
    
    # Randomly select half to modify
    num_to_modify = len(indices_to_modify) // 2
    indices_to_change = random.sample(indices_to_modify, num_to_modify)
    
    # Apply random replacements
    for idx in indices_to_change:
        block_names[idx] = random.choice(replacement_options)

def process_json_file(filepath):
    """Process a single RMB.json file."""
    with open(filepath, 'r') as file:
        data = json.load(file)
    
    # Only process files where LocationType is TownHamlet
    if data.get("MapTableData", {}).get("LocationType") == "TownHamlet":
        exterior_data = data.get("Exterior", {}).get("ExteriorData", {})
        block_names = exterior_data.get("BlockNames", [])
        
        if block_names:
            modify_genras_elements(block_names)
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

