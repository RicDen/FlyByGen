from itertools import product, combinations


def generate_value_combo_list(params, increments):
    generated_values = []
    for param in params:
        if isinstance(increments[param], float) or isinstance(increments[param], int):
            generated_values.append(generate_values_from_range(params[param], increments[param]))
        elif isinstance(params[param], list):
            print("Vector in form of list provided")
            vector = []
            for (i, value) in enumerate(params[param]):
                vector.append(generate_values_from_range(value, increments[param][i]))
            permutations = [list(perm) for perm in product(*vector)]
            generated_values.append(permutations)
            # and created all list option
        else:
            print("Error: Invalid parameters")
    return product(*generated_values)

def assign_value_names(parameter_combinations, params):
    value_combinations = []

    # Iterate over each parameter combination
    for param_values in parameter_combinations:
        object_value = {}

        # Map each parameter to its corresponding value in the combination
        for param, value in zip(params, param_values):
            object_value[param] = value

        # Append the resulting dictionary to the list of value combinations
        value_combinations.append(object_value)

    return value_combinations

def generate_config_combinations(object_values):
    permutations = list(product(*object_values.values()))
    return [dict(zip(object_values.keys(), p)) for p in permutations]
    # permutations =  [list(perm) for perm in product(*object_values)]
    return permutations

def generate_parameter_combinations(parameter_ranges, increments):
    combo_dict = {}
    first_layer_entries = {}
    first_layer_entries["range"] = {}
    first_layer_entries["increments"] = {}
    recursion = False
    parameter = False
    for key, value in increments.items():
        if isinstance(value, dict):
            recursion = True
            combo_dict[key] = generate_parameter_combinations(parameter_ranges[key], increments[key])
        else:
            parameter = True
            first_layer_entries["range"][key] = parameter_ranges[key]
            first_layer_entries["increments"][key] = increments[key]

    if recursion:
        recursive_list = generate_config_combinations(combo_dict)

    if parameter:
        if parameter_ranges != first_layer_entries["range"]:
            print("Creating first layer combos")
            first_layer_parameter_value_combinations = generate_value_combo_list(first_layer_entries["range"], first_layer_entries["increments"])
            first_layer_combo_list = assign_value_names(first_layer_parameter_value_combinations, first_layer_entries["range"])
            recursive_list = [{**dict1, **dict2} for dict1, dict2 in product(first_layer_combo_list, recursive_list)]

        if len(combo_dict) == 0:
            recursive_parameter_value_combinations = generate_value_combo_list(parameter_ranges, increments)
            recursive_list = assign_value_names(recursive_parameter_value_combinations, parameter_ranges)

    return recursive_list
# Helper function to generate values
def generate_values_from_range(param, increment):
    min_value = param.get('min', 0)
    max_value = param.get('max', 0)
    current_value = min_value
    values = []
    while current_value <= max_value:
        values.append(current_value)
        if isinstance(current_value,dict):
            break;
        else:
            current_value += increment
    return values




# # Example usage 1: Normal int/float values for nucleus generator:
# parameter_ranges_nucleus = {
#     'core': {'radius': {'min': 1.5, 'max':2.5}, 'length': {'min': 1.0, 'max': 3.0}},
#     'addon1': {'min': 1.5, 'max': 2.5}
# }
#
# increments_nucleus = {
#     'core': {'radius': 1.0, 'length': 1.0},
#     'addon1': 1.0
# }
#
# print("Simple nucleus parameter range testing:")
# combinations_nucleus = generate_parameter_combinations(parameter_ranges_nucleus, increments_nucleus)
# print("Combination of all objects within the range:")
# for combination in combinations_nucleus:
#     print(f"{combination}")


# # Example usage 2: Normal int/float values and array handling for nucleus generator:
#
# parameter_ranges_nucleus_array = {
#     'core': {'radius': {'min': 1.0, 'max': 3.0}, 'rotation': [{'min': 1.0, 'max': 2.0}, {'min': 2.0, 'max': 3.0}, {'min': 2.0, 'max': 4.0}]},
#     'addon1': {'radius': {'min': 1.5, 'max': 2.5}, 'length': {'min': 1.0, 'max': 3.0}}
# }
#
# increments_nucleus_array = {
#     'core': {'radius': 1.0, 'rotation': [1.0, 1.0, 1.0]},
#     'addon1': {'radius': 1.0, 'length': 1.0}
# }
#
# print("Array handling for nucleus parameter range testing:")
# combinations_nucleus_array = generate_parameter_combinations(parameter_ranges_nucleus_array, increments_nucleus_array)
# print("Combination of all objects within the range:")
# for combination in combinations_nucleus_array:
#     print(f"{combination}")

# Example usage 3:  Normal values with other levels of nexted than core, for example animation:
parameter_ranges_animation ={
    "fps": {'min': 22, 'max': 25},
    "rotation_parameters": {
        "B2_main_rotation": {
            "period": {'min': 3, 'max': 5}
        }
    },
    "fly_by_parameters": {
        "speed": {'min': 75, 'max': 85},
        "t_start": {'min': -1230, 'max': -1110}
    }
}

increments_animation ={
    "fps": 1,
    "rotation_parameters": {
        "B2_main_rotation": {
            "period": 1
        }
    },
    "fly_by_parameters": {
        "speed": 5,
        "t_start": 10
    }
}

print("Simple nucleus parameter range testing:")
combinations_animation = generate_parameter_combinations(parameter_ranges_animation, increments_animation)
print("Combination of all objects within the range:")
for combination in combinations_animation:
    print(f"{combination}")
