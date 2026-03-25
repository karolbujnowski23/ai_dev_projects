import json

def check_file_name():
    '''validate the presence of files and their JSON format, returning a list of any files that were not found or had JSON errors.'''
    unsuccessful_loads = []
    for i in range(1, 9999):
        file_name = f'./sensors/{i:04d}.json'
        try:
            with open(file_name, 'r') as f:
                data = json.load(f)
                # print(f"Successfully loaded {file_name}")
        except FileNotFoundError:
            unsuccessful_loads.append(file_name)
            # print(f"File not found: {file_name}")
        except json.JSONDecodeError:
            print(f"Invalid JSON format in file: {file_name}")
    return unsuccessful_loads
# check successfully loaded files and print any that were not found or had JSON errors.

def simple_read(file_nr):
    file_name = f'./sensors/{file_nr:04d}.json'
    with open(file_name, 'r') as f:
        data = json.load(f)
    # return print(json.dumps(data, indent=2))
    return data

def get_unique_sensor_types():
    sensor_types = set()
    for i in range(1, 10000):
        try:
            data = simple_read(i)
            sensor_types.add(data["sensor_type"])
        except FileNotFoundError:
            print(f"File not found: {i:04d}.json")
        except json.JSONDecodeError:
            print(f"Invalid JSON format in file: {i:04d}.json")
    return sensor_types

def initial_sensors_check(sensor_data):
    if not sensor_data:
        return False

    # Mapping of sensor_type components to their data keys
    type_mapping = {
        "temperature": "temperature_K",
        "pressure": "pressure_bar",
        "water": "water_level_meters",
        "voltage": "voltage_supply_v",
        "humidity": "humidity_percent"
    }

    ranges = {
        "temperature_K": (553, 873),
        "pressure_bar": (60, 160),
        "water_level_meters": (5.0, 15.0),
        "voltage_supply_v": (229.0, 231.0),
        "humidity_percent": (40.0, 80.0)
    }

    # Determine which keys are expected based on sensor_type
    sensor_type = sensor_data.get("sensor_type", "")
    type_components = sensor_type.split('/')
    expected_keys = {type_mapping[comp] for comp in type_components if comp in type_mapping}

    for key, (min_val, max_val) in ranges.items():
        value = sensor_data.get(key)
        
        if key in expected_keys:
            # Condition: If it's an expected key and not 0, it must be in range
            if value is not None and value != 0:
                if not (min_val <= value <= max_val):
                    return False
        else:
            # Condition: If it's NOT an expected key, it must be 0 or None
            if value is not None and value != 0:
                
                return False
            
    return True

def clafify_sensors_status() -> dict:
    ok = 0
    not_ok = 0
    sensors = {}
    for i in range(1, 10000):
        try:
            data = simple_read(i)
            if initial_sensors_check(data):
                # print(f"File {file_name} passed the initial sensor check.")
                sensors.update({f"{i:04d}":{"operator_notes":data["operator_notes"],"status":"OK"}})
                ok+=1    
            else:
                # print(f"File {file_name} failed the initial sensor check.")
                sensors.update({f"{i:04d}":{"operator_notes":data["operator_notes"],"status":"FAILED"}})
                not_ok+=1
        except FileNotFoundError:
            print(f"File not found: {i:04d}.json")
            sensors.update({f"{i:04d}":{"operator":None,"status":"NOT FOUND"}})
        except json.JSONDecodeError:
            print(f"Invalid JSON format in file: {i:04d}.json")
            sensors.update({f"{i:04d}":{"operator":None,"status":"INVALID JSON"}})
    print(f"Total OK: {ok}, Total FAILED: {not_ok}")        
    return sensors




def main():
    sensors_status = clafify_sensors_status()
    first_n = dict(list(sensors_status.items())[:20])
    print(json.dumps(first_n, indent=2))

    # sensor_types = get_unique_sensor_types()
    # print("sensor types: "+", ".join(sensor_types))
    # print("sensor types count: "+str(len(sensor_types)))
    


# TODO: add rules that also detect the anomalies from the sensors itself not only operator


if __name__ == "__main__":
    # print(check_file_name())
    # main("0001")
    # failed=['0158', '0307', '0516', '0567', '0753', '1053', '1269', '1632', '1678', '1819', '2044', '2175', '2238', '2437', '2500', '2958', '3123', '3713', '3798', '4040', '4186', '4237', '4630', '4673', '4888', '5022', '5156', '5405', '5714', '5715', '5799', '6197', '6281', '6336', '6778', '7266', '7680', '7701', '8076', '8168', '8410', '8457', '9151', '9288', '9422', '9518', '9583', '9604', '9848']
    # for i in failed[:10]:
    #     print(json.dumps(simple_read(int(i)), indent=2))

    # main("0002")
    main()



