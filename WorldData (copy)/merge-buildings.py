import json
import os
import re


def preprocess_json(raw_content, placeholder="__BACKSLASH__"):
    return raw_content.replace("\\", placeholder)


def postprocess_json(processed_content, placeholder="__BACKSLASH__"):
    return processed_content.replace(placeholder, "\\")


def load_json_file(file_path, placeholder="__BACKSLASH__"):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            raw_content = file.read()
            preprocessed_content = preprocess_json(raw_content, placeholder)
            return json.loads(preprocessed_content)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON file '{file_path}'. {e}")
    except Exception as e:
        print(f"Error: Unexpected error while reading file '{file_path}'. {e}")
    return None


def save_json_file(file_path, data, placeholder="__BACKSLASH__"):
    try:
        json_content = json.dumps(data, indent=4)
        postprocessed_content = postprocess_json(json_content, placeholder)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(postprocessed_content)
        print(f"Successfully saved file '{file_path}'.")
    except Exception as e:
        print(f"Error: Failed to save JSON file '{file_path}'. {e}")


def replace_building(rmb_file, building_file, position):
    placeholder = "__BACKSLASH__"

    # Load RMB JSON
    rmb_data = load_json_file(rmb_file, placeholder)
    if not rmb_data:
        return

    # Load building JSON
    building_data = load_json_file(building_file, placeholder)
    if not building_data:
        return

    # Validate position
    if "RmbBlock" not in rmb_data or "FldHeader" not in rmb_data["RmbBlock"]:
        print(f"Error: Invalid RMB JSON structure in '{rmb_file}'.")
        return

    building_list = rmb_data["RmbBlock"]["FldHeader"].get("BuildingDataList", [])
    sub_records = rmb_data["RmbBlock"].get("SubRecords", [])

    if position < 0 or position >= len(building_list) or position >= len(sub_records):
        print(f"Error: Position {position} is out of range in '{rmb_file}'.")
        return

    # Replace in BuildingDataList
    original_building = building_list[position]
    building_list[position] = {
        "FactionId": building_data.get("FactionId", original_building.get("FactionId")),
        "BuildingType": building_data.get("BuildingType", original_building.get("BuildingType")),
        "Quality": building_data.get("Quality", original_building.get("Quality")),
        "NameSeed": building_data.get("NameSeed", original_building.get("NameSeed")),
    }

    # Only update FactionId if the original value is 0
    if original_building.get("FactionId") != 0:
        building_list[position]["FactionId"] = original_building.get("FactionId")

    # Replace in SubRecords
    original_subrecord = sub_records[position]
    updated_subrecord = original_subrecord.copy()

    # Replace only the "Exterior" and "Interior" parts
    rmb_sub_record = building_data.get("RmbSubRecord", {})
    if "Exterior" in rmb_sub_record:
        updated_exterior = original_subrecord.get("Exterior", {}).copy()
        updated_exterior.update(
            {
                key: value
                for key, value in rmb_sub_record.get("Exterior", {}).items()
                if key not in {"XPos", "ZPos", "YRotation"}
            }
        )
        updated_subrecord["Exterior"] = updated_exterior

    if "Interior" in rmb_sub_record:
        updated_subrecord["Interior"] = rmb_sub_record["Interior"]

    sub_records[position] = updated_subrecord

    # Save the updated RMB JSON
    save_json_file(rmb_file, rmb_data, placeholder)


def process_directory():
    # Find all *.RMB.json files
    rmb_files = [file for file in os.listdir() if file.endswith(".RMB.json") and not file.endswith(".meta")]

    # Ensure the buildings subdirectory exists
    buildings_dir = "buildings"
    if not os.path.isdir(buildings_dir):
        print(f"Error: The '{buildings_dir}' subdirectory does not exist.")
        return

    # Find all building replacement files in the buildings subdirectory
    building_files = [
    file for file in os.listdir(buildings_dir)
    if re.match(r".*\.RMB-\d+-building\d+\.json", file) and not file.endswith(".meta")]

    # Group building replacement files by their RMB prefix
    building_replacements = {}
    for building_file in building_files:
        match = re.match(r"(.*\.RMB)-\d+-building(\d+)\.json", building_file)
        if match:
            prefix = match.group(1)
            index = int(match.group(2))
            building_replacements.setdefault(prefix, []).append((os.path.join(buildings_dir, building_file), index))

    # Apply replacements
    for rmb_file in rmb_files:
        prefix = rmb_file.replace(".json", "")
        if prefix in building_replacements:
            for building_file, index in building_replacements[prefix]:
                print(f"Applying replacement: {building_file} -> {rmb_file} at position {index}")
                replace_building(rmb_file, building_file, index)


if __name__ == "__main__":
    process_directory()

