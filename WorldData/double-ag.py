import os
import json
import re

TARGET_BLOCK_1 = "GENRBM00.RMB"
TARGET_BLOCK_2 = "RESIGS04.RMB"

def fix_invalid_escapes(json_string):
    """Escape invalid backslashes in the JSON string."""
    return re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', json_string)

def load_json_safe(filepath):
    """Load a JSON file with invalid escape handling."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            raw = f.read()
        fixed = fix_invalid_escapes(raw)
        return json.loads(fixed)
    except Exception as e:
        print(f"Failed to read {filepath}: {e}")
        return None

def get_block_names(data):
    """Extract BlockNames list from the JSON data, if present."""
    return data.get("Exterior", {}).get("ExteriorData", {}).get("BlockNames", [])

def main():
    matched_files = []

    for filename in os.listdir("."):
        if not filename.endswith(".json"):
            continue

        data = load_json_safe(filename)
        if data is None:
            continue

        block_names = get_block_names(data)
        if TARGET_BLOCK_1 in block_names and TARGET_BLOCK_2 in block_names:
            matched_files.append(filename)

    # Print results
    print(f"\nFiles containing BOTH {TARGET_BLOCK_1} and {TARGET_BLOCK_2}:")
    for fname in matched_files:
        print(f"- {fname}")

if __name__ == "__main__":
    main()

