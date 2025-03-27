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

def fix_invalid_escapes(json_string):
    """Escape invalid backslashes in the JSON string."""
    # Replace backslashes not followed by valid escape characters
    return re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', json_string)

def process_json_file(filepath):
    """Process a single RMB.json file."""
    with open(filepath, 'r', encoding='utf-8') as file:
        raw = file.read()
    
    # Preprocess to fix invalid escape sequences
    fixed_raw = fix_invalid_escapes(raw)

    try:
        data = json.loads(fixed_raw)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON in {filepath}: {e}")
        return

    # Skip TownHamlet locations
    if data.get("MapTableData", {}).get("LocationType") != "TownHamlet":
        exterior_data = data.get("Exterior", {}).get("ExteriorData", {})
        block_names = exterior_data.get("BlockNames", [])

        if block_names:
            replace_tempba_with_tempbs(block_names)
            exterior_data["BlockNames"] = block_names  # Update in place

        # Write the modified data back to the file
        with open(filepath, 'w', encoding='utf-8') as file:
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

