import json
import os
import glob
import re
import random

# Map BuildingType names to enum values
BUILDING_TYPE_ENUM = {
    "None": -1,
    "Alchemist": 0,
    "HouseForSale": 1,
    "Armorer": 2,
    "Bank": 3,
    "Town4": 4,
    "Bookseller": 5,
    "ClothingStore": 6,
    "FurnitureStore": 7,
    "GemStore": 8,
    "GeneralStore": 9,
    "Library": 10,
    "GuildHall": 11,
    "PawnShop": 12,
    "WeaponSmith": 13,
    "Temple": 14,
    "Tavern": 15,
    "Palace": 16,
    "House1": 17,
    "House2": 18,
    "House3": 19,
    "House4": 20,
    "House5": 21,
    "House6": 22,
    "Town23": 23,
    "Ship": 24,
    "Special1": 0x74,
    "Special2": 0xdf,
    "Special3": 0xf9,
    "Special4": 0xfa,
    "AnyShop": 0xfffd,
    "AnyHouse": 0xfffe,
    "AllValid": 0xffff,
}

# Map numeric BuildingType values to their string equivalents
ENUM_TO_BUILDING_TYPE = {v: k for k, v in BUILDING_TYPE_ENUM.items()}


def load_json_file(filepath):
    """Safely load a JSON file with escape sequence handling."""
    with open(filepath, 'r') as f:
        content = f.read()
        content = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', content)  # Fix invalid escapes
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in file {filepath}: {e}")
            return None


def normalize_building_type(building_type):
    """Convert BuildingType to its string equivalent."""
    if isinstance(building_type, int):
        return ENUM_TO_BUILDING_TYPE.get(building_type, "None")  # Default to "None"
    return building_type  # Assume it's already a string


def count_interiors(rmb_data):
    """Count the number of Interior subrecords in an RMB block."""
    sub_records = rmb_data.get('RmbBlock', {}).get('SubRecords', [])
    return sum(1 for record in sub_records if 'Interior' in record)


def get_vanilla_building_data(location_name):
    """Extract NameSeed, Quality, and Sector data from the vanilla location JSON."""
    vanilla_file = os.path.join('vanillaloc', location_name)
    if not os.path.exists(vanilla_file):
        print(f"  Vanilla file {vanilla_file} does not exist.")
        return {}, {}, {}

    vanilla_data = load_json_file(vanilla_file)
    if vanilla_data is None:
        return {}, {}, {}

    # Extract building data from vanilla file
    vanilla_buildings = vanilla_data.get('Exterior', {}).get('Buildings', [])
    name_seed_list = {}
    quality_list = {}
    sector_list = {}

    for building in vanilla_buildings:
        building_type = normalize_building_type(building.get('BuildingType'))

        name_seed = building.get('NameSeed')
        quality = building.get('Quality')
        sector = building.get('Sector')

        # Initialize lists for this building type
        if building_type not in name_seed_list:
            name_seed_list[building_type] = []
            quality_list[building_type] = []
            sector_list[building_type] = []

        # Append data to respective lists
        if name_seed is not None:
            name_seed_list[building_type].append(name_seed)
        if quality is not None:
            quality_list[building_type].append(quality)
        if sector is not None:
            sector_list[building_type].append(sector)

    return name_seed_list, quality_list, sector_list

def update_buildings():
    """Update buildings in all location JSON files with vanilla data."""
    # Get all location JSON files
    location_files = glob.glob('location*.json')

    for location_file in location_files:
        print(f"Processing {location_file}")
        
        # Load the location data
        location_data = load_json_file(location_file)
        if location_data is None:
            continue

        # Extract the LocationId
        location_id = location_data.get('Exterior', {}).get('RecordElement', {}).get('Header', {}).get('LocationId')
        if location_id is None:
            print(f"  No LocationId found in {location_file}. Skipping.")
            continue

        # Extract the BlockNames array
        block_names = location_data.get('Exterior', {}).get('ExteriorData', {}).get('BlockNames', [])
        if not block_names:
            print(f"  No BlockNames found in {location_file}.")
            continue

        # Load the vanilla location data
        location_name = os.path.basename(location_file)
        name_seed_list, quality_list, sector_list = get_vanilla_building_data(location_name)

        # Create a dictionary for matching BuildingType and FactionId
        vanilla_data_by_type_faction = {}
        for building_type, name_seeds in name_seed_list.items():
            for i, name_seed in enumerate(name_seeds):
                # Normalize FactionId: Treat 26 and 92 as the same
                faction_id = 0
                if sector_list.get(building_type) and i < len(sector_list[building_type]):
                    faction_id = sector_list[building_type][i]
                    if faction_id == 92:
                        faction_id = 26

                vanilla_data_by_type_faction[(building_type, faction_id)] = {
                    "NameSeed": name_seed,
                    "Quality": quality_list[building_type][i] if quality_list.get(building_type) and i < len(quality_list[building_type]) else None,
                    "Sector": sector_list[building_type][i] if sector_list.get(building_type) and i < len(sector_list[building_type]) else None,
                }

        # Determine the global maximum Sector value
        global_max_sector = max(
            (max(sectors) for sectors in sector_list.values() if sectors), 
            default=0
        )

        new_buildings = []
        used_sectors = set()  # Track used sectors to ensure uniqueness

        # Process each block in BlockNames
        for block_name in block_names:
            rmb_file = block_name + '.json'
            print(f"  Processing block: {block_name}")

            # Load the RMB data
            rmb_data = load_json_file(rmb_file)
            if rmb_data is None:
                print(f"    Missing or invalid RMB file: {rmb_file}")
                continue

            # Extract building data
            building_data_list = rmb_data.get('RmbBlock', {}).get('FldHeader', {}).get('BuildingDataList', [])
            num_interiors = count_interiors(rmb_data)
            buildings_to_add = building_data_list[:num_interiors]

            # Update building data
            for building in buildings_to_add:
                building_type = normalize_building_type(building.get('BuildingType'))
                faction_id = building.get('FactionId', 0)

                # Normalize FactionId for matching
                normalized_faction_id = 26 if faction_id in {26, 92} else faction_id

                # First try to match BuildingType and normalized FactionId
                key = (building_type, normalized_faction_id)
                vanilla_data = vanilla_data_by_type_faction.get(key)

                # If no exact match, fallback to match BuildingType only
                if not vanilla_data and name_seed_list.get(building_type):
                    vanilla_data = {
                        "NameSeed": name_seed_list[building_type].pop(0) if name_seed_list[building_type] else None,
                        "Quality": quality_list[building_type].pop(0) if quality_list.get(building_type) else None,
                        "Sector": sector_list[building_type].pop(0) if sector_list.get(building_type) else None,
                    }

                # Assign NameSeed
                if vanilla_data and vanilla_data["NameSeed"] is not None:
                    building["NameSeed"] = vanilla_data["NameSeed"]
                else:
                    building["NameSeed"] = random.randint(0, 30000)

                # Assign Quality
                if vanilla_data and vanilla_data["Quality"] is not None:
                    building["Quality"] = vanilla_data["Quality"]
                else:
                    building["Quality"] = building.get("Quality")  # Fallback to RMB quality

                # Assign Sector
                if vanilla_data and vanilla_data["Sector"] is not None:
                    sector = vanilla_data["Sector"]
                else:
                    # Increment from the global maximum Sector
                    while global_max_sector in used_sectors:
                        global_max_sector += 3
                    sector = global_max_sector
                    global_max_sector = sector  # Update the global max

                building["Sector"] = sector
                used_sectors.add(sector)  # Track the used sector

                # Assign LocationId
                building["LocationId"] = location_id

                # Always set FactionId to 26 for 26 or 92
                if faction_id in {26, 92}:
                    building["FactionId"] = 26

                # Add to the new buildings list
                new_buildings.append(building)

        # Update the location file's building data
        location_data["Exterior"]["Buildings"] = new_buildings
        location_data["Exterior"]["BuildingCount"] = len(new_buildings)

        # Save the updated location JSON
        with open(location_file, "w") as f:
            json.dump(location_data, f, indent=4)

        print(f"  Updated {location_file} with {len(new_buildings)} buildings.")

if __name__ == '__main__':
    update_buildings()


