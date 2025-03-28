import os
import json
import pandas as pd
import re

# Define substrings for filenames that require only removal
remove_only_keywords = {
    "BL", "BM", "BS", "GL", "GM", "GS", "FARMBA", "CAST", "PALA", 
    "CUSTGA", "DUNG", "GRVE", "MARKAB", "RUIN", "SHCKBA", "SHIP", 
    "TEMPB", "TEMPG", "WITC", "MAGEBA", "MAGEGA"
}

def remove_entries(json_data):
    remove_ids = {52990, 52991, 45074, 45075, 45076, 45077}
    
    def filter_records(records):
        return [record for record in records if record.get('ModelIdNum') not in remove_ids]

    if "RmbBlock" in json_data and "SubRecords" in json_data["RmbBlock"]:
        for sub_record in json_data["RmbBlock"]["SubRecords"]:
            if "Exterior" in sub_record:
                sub_record["Exterior"]["Block3dObjectRecords"] = filter_records(sub_record["Exterior"]["Block3dObjectRecords"])
            if "Interior" in sub_record:
                sub_record["Interior"]["Block3dObjectRecords"] = filter_records(sub_record["Interior"]["Block3dObjectRecords"])

    if "RmbSubRecord" in json_data and "Exterior" in json_data["RmbSubRecord"]:
        json_data["RmbSubRecord"]["Exterior"]["Block3dObjectRecords"] = filter_records(json_data["RmbSubRecord"]["Exterior"]["Block3dObjectRecords"])
    if "RmbSubRecord" in json_data and "Interior" in json_data["RmbSubRecord"]:
        json_data["RmbSubRecord"]["Interior"]["Block3dObjectRecords"] = filter_records(json_data["RmbSubRecord"]["Interior"]["Block3dObjectRecords"])

    return json_data

def sanitize_json_string(json_string):
    sanitized_string = json_string.replace('\\', '')
    return sanitized_string

# Process JSON files
for filename in os.listdir('.'):
    if filename.endswith('.json'):
        # Check if the filename contains any of the keywords
        remove_only = any(keyword in filename for keyword in remove_only_keywords)
        print(f"Processing file: {filename} (Remove Only: {remove_only})")

        try:
            with open(filename, 'r') as file:
                json_string = file.read()
                sanitized_string = sanitize_json_string(json_string)
                data = json.loads(sanitized_string)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON file {filename}: {e}")
            continue
        
        # Apply removal logic
        updated_data = remove_entries(data)
        
        # If not "remove-only," add new entries (skip for specified filenames)
        if not remove_only:
            try:
                building_dimensions = pd.read_csv('BuildingDimensions.csv')
                if 'ModelId' in building_dimensions.columns:
                    building_dimensions.set_index('ModelId', inplace=True)
                updated_data = add_new_entries(updated_data, building_dimensions)
            except Exception as e:
                print(f"Error reading CSV file or adding entries: {e}")
                continue
        
        # Write updated JSON back to the file
        with open(filename, 'w') as file:
            json.dump(updated_data, file, indent=4)

        print(f"Processed and updated: {filename}")

print("All JSON files processed.")

