import json
import os
import logging

logger = logging.getLogger("Orchestrator")

# Constants for ranges
SENSOR_RANGES = {
    "temperature_K": (553, 873),
    "pressure_bar": (60, 160),
    "water_level_meters": (5.0, 15.0),
    "voltage_supply_v": (229.0, 231.0),
    "humidity_percent": (40.0, 80.0)
}

# Mapping of sensor_type components to their data keys
TYPE_MAPPING = {
    "temperature": "temperature_K",
    "pressure": "pressure_bar",
    "water": "water_level_meters",
    "voltage": "voltage_supply_v",
    "humidity": "humidity_percent"
}

def validate_technical_data(sensor_data):
    """
    Checks if sensor data complies with technical specs:
    - Active sensors (based on sensor_type) must be within range and non-zero.
    - Inactive sensors must be exactly zero.
    Returns: (bool is_ok, str reason)
    """
    if not sensor_data:
        return False, "Missing sensor data"

    sensor_type = sensor_data.get("sensor_type", "")
    type_components = sensor_type.split('/')
    expected_keys = {TYPE_MAPPING[comp] for comp in type_components if comp in TYPE_MAPPING}

    # Verify each sensor field
    for key, (min_val, max_val) in SENSOR_RANGES.items():
        value = sensor_data.get(key)
        
        if key in expected_keys:
            # Active sensor must be in range (which implies non-zero as ranges > 0)
            if value is None or value == 0:
                return False, f"Active sensor {key} is zero or missing."
            if not (min_val <= value <= max_val):
                return False, f"Active sensor {key} ({value}) is out of range ({min_val}-{max_val})."
        else:
            # Inactive sensor MUST be zero
            if value is not None and value != 0:
                return False, f"Inactive sensor {key} ({value}) should be zero."

    return True, "OK"

def load_all_sensors(sensors_dir):
    """
    Loads all JSON files from the sensors directory.
    Returns: dict mapping sensor_id -> (data_dict or None if error, technical_status)
    """
    sensors_info = {}
    logger.info(f"Loading sensors from {sensors_dir}")
    
    # Files are 0001.json to 9999.json
    for i in range(1, 10000):
        file_id = f"{i:04d}"
        file_path = os.path.join(sensors_dir, f"{file_id}.json")
        
        if not os.path.exists(file_path):
            # Not found is not an anomaly mentioned, but let's log it
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                is_ok, reason = validate_technical_data(data)
                sensors_info[file_id] = {
                    "data": data,
                    "technical_status": "OK" if is_ok else "FAILED",
                    "technical_reason": reason
                }
        except json.JSONDecodeError:
            logger.warning(f"File {file_id}.json has invalid JSON.")
            sensors_info[file_id] = {
                "data": None,
                "technical_status": "FAILED",
                "technical_reason": "INVALID JSON"
            }
        except Exception as e:
            logger.error(f"Error reading {file_id}.json: {e}")
            
    logger.info(f"Loaded {len(sensors_info)} sensor files.")
    return sensors_info
