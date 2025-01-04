import os
import json

def is_corner(index, width, height):
    """Check if an index is a corner in a 2D grid."""
    return index in {0, width - 1, (height - 1) * width, height * width - 1}

def is_adjacent_to_farm(block_names, index, width):
    """Check if an index is adjacent to a FARMAA or FARMBA element."""
    farm_prefixes = ("FARMAA", "FARMBA")
    row, col = divmod(index, width)
    adjacent_indices = [
        index - 1 if col > 0 else None,  # Left
        index + 1 if col < width - 1 else None,  # Right
        index - width if row > 0 else None,  # Above
        index + width if row < (len(block_names) // width) - 1 else None  # Below
    ]
    return any(block_names[adj_idx].startswith(farm_prefixes) for adj_idx in adjacent_indices if adj_idx is not None)

def modify_blocknames(block_names, width, height):
    """Modify BlockNames array based on rules."""
    for idx, block_name in enumerate(block_names):
        if block_name.startswith(("GENRAM", "TEMPAA", "TVRNAM")):
            if is_corner(idx, width, height) or is_adjacent_to_farm(block_names, idx, width):
                block_names[idx] = block_name.replace("GENRAM", "GENRAS").replace("TEMPAA", "TEMPAS").replace("TVRNAM", "TVRNAS")

def process_json_file(filepath):
    """Process a single RMB.json file."""
    with open(filepath, 'r') as file:
        data = json.load(file)
    
    if data.get("MapTableData", {}).get("LocationType") == "TownHamlet":
        exterior_data = data.get("Exterior", {}).get("ExteriorData", {})
        block_names = exterior_data.get("BlockNames", [])
        width = exterior_data.get("Width", 0)
        height = exterior_data.get("Height", 0)
        
        if block_names and width and height:
            modify_blocknames(block_names, width, height)
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

