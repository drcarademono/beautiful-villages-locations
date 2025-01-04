import os
import json
import pandas as pd
import re

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

def add_new_entries(json_data, building_dimensions):
    building_dimensions.index = building_dimensions.index.map(str)
    
    def find_max_y_and_rotation(exterior_records):
        max_y = float('-inf')
        max_y_rotation = 0
        exterior_y_pos = 0
        max_model_id = None
        for record in exterior_records:
            model_id = record.get("ModelId")
            if model_id and str(model_id) in building_dimensions.index:
                y_value = building_dimensions.loc[str(model_id), "Y"]
                if y_value > max_y:
                    max_y = y_value
                    max_y_rotation = record.get("YRotation", 0)
                    exterior_y_pos = record.get("YPos", 0)
                    max_model_id = str(model_id)
        return max_y, max_y_rotation, exterior_y_pos, max_model_id

    def process_subrecord(sub_record):
        if "Interior" in sub_record and "Exterior" in sub_record:
            interior_records = sub_record["Interior"]["Block3dObjectRecords"]
            exterior_records = sub_record["Exterior"]["Block3dObjectRecords"]

            matching_interior = any(record.get("ModelIdNum") in {41116, 41117} and record.get("YPos", 0) >= -100 for record in interior_records)
            
            if matching_interior:
                max_y_value, max_y_rotation, exterior_y_pos, max_model_id = find_max_y_and_rotation(exterior_records)
                model_offset = building_dimensions.loc[max_model_id, "ModelOffset"] if max_model_id in building_dimensions.index else 0
                print(f"ModelId: {max_model_id}, ModelOffset: {model_offset}")
                print(f"ModelId: {max_model_id}, ExteriorYPos: {exterior_y_pos}")

                if pd.isna(max_y_value):
                    max_y_value = 0
                if pd.isna(exterior_y_pos):
                    exterior_y_pos = 0
                if pd.isna(model_offset):
                    model_offset = 0

                for interior_record in interior_records:
                    if interior_record.get("ModelIdNum") in {41116, 41117} and interior_record.get("YPos", 0) >= -100:
                        new_record_52991 = interior_record.copy()
                        new_record_52991["ModelId"] = "52991"
                        new_record_52991["ModelIdNum"] = 52991
                        new_record_52991["ObjectType"] = 4
                        new_record_52991["YRotation"] = max_y_rotation
                        if max_y_value != float('-inf'):
                            if max_y_value <= 220:
                                new_record_52991["YPos"] = int(-(max_y_value + 20 - exterior_y_pos + model_offset))
                            elif max_y_value >= 300:
                                new_record_52991["YPos"] = int(-(max_y_value - 80 - exterior_y_pos + model_offset))
                            else:
                                new_record_52991["YPos"] = int(-(max_y_value - exterior_y_pos + model_offset))
                        else:
                            new_record_52991["YPos"] = 0
                        
                        exterior_records.append(new_record_52991)
                        
                        new_record_45077 = new_record_52991.copy()
                        new_record_45077["ModelId"] = "45077"
                        new_record_45077["ModelIdNum"] = 45077
                        new_record_45077["YPos"] += 129
                        new_record_45077["XScale"] = 0.9
                        new_record_45077["ZScale"] = 0.9
                        exterior_records.append(new_record_45077)
                        
                        current_y_pos = new_record_45077["YPos"]
                        while current_y_pos <= 0:
                            new_record_45076 = new_record_45077.copy()
                            new_record_45076["ModelId"] = "45076"
                            new_record_45076["ModelIdNum"] = 45076
                            new_record_45076["YPos"] = current_y_pos + 114
                            new_record_45076["XScale"] = 0.9
                            new_record_45076["ZScale"] = 0.9
                            exterior_records.append(new_record_45076)
                            
                            current_y_pos += 114
                            if current_y_pos > 0:
                                break

                sub_record["Exterior"]["Header"]["Num3dObjectRecords"] = len(exterior_records)

    if "RmbBlock" in json_data and "SubRecords" in json_data["RmbBlock"]:
        for sub_record in json_data["RmbBlock"]["SubRecords"]:
            process_subrecord(sub_record)
    elif "RmbSubRecord" in json_data:
        process_subrecord(json_data["RmbSubRecord"])

    return json_data

def sanitize_json_string(json_string):
    sanitized_string = json_string.replace('\\', '')
    return sanitized_string

try:
    building_dimensions = pd.read_csv('BuildingDimensions.csv')
    if 'ModelId' in building_dimensions.columns:
        building_dimensions.set_index('ModelId', inplace=True)
    else:
        print("ModelId column not found in the CSV file. Columns available are:", building_dimensions.columns.tolist())
except Exception as e:
    print(f"Error reading CSV file: {e}")

for filename in os.listdir('.'):
    if filename.endswith('.json'):
        print(f"Processing file: {filename}")
        try:
            with open(filename, 'r') as file:
                json_string = file.read()
                sanitized_string = sanitize_json_string(json_string)
                data = json.loads(sanitized_string)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON file {filename}: {e}")
            continue
        
        updated_data = remove_entries(data)
        updated_data = add_new_entries(updated_data, building_dimensions)
        
        with open(filename, 'w') as file:
            json.dump(updated_data, file, indent=4)

        print(f"Processed and updated: {filename}")

print("All JSON files processed.")

