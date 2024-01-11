from itertools import product


def generate_parameter_value_combinations(obj_name, params, increments):
    generated_values = []
    for param in params:
        if isinstance(params[param], dict):
            generated_values.append(generate_values_from_range(params[param], increments[obj_name][param]))
        elif isinstance(params[param], list):
            print("Vector in form of list provided")
            vector = []
            for (i, value) in enumerate(params[param]):
                vector.append(generate_values_from_range(value, increments[obj_name][param][i]))
            # permutations = list(product(*vector))
            permutations = [list(perm) for perm in product(*vector)]
            generated_values.append(permutations)
            # and created all list option
        else:
            print("Error: Invalid parameters")
    # parameter_combinations = product(
    #     *[generate_values(params[param], increments[obj_name][param]) for param in params])
    return product(*generated_values)

def assign_value_names(parameter_combinations, params):
    """
        Generates a list of dictionaries containing the combination of parameters value with their name
        Parameters:
        - parameter_combinations (list): List of parameter combinations obtained from itertools.product.
        - params (list): List of parameter names.

        Returns:
        - list: List of dictionaries representing value combinations for each parameter set.

        Example:
        ```python
        parameter_combinations = [(1.0, 2.0), (3.0, 4.0)]
        params = ['radius', 'length']
        result = generate_values_combinations(parameter_combinations, params)
        ```
        Result:
        ```python
        [{'radius': 1.0, 'length': 2.0}, {'radius': 3.0, 'length': 4.0}]
        ```
    """
    value_combinations = []

    # Iterate over each parameter combination
    for param_values in parameter_combinations:
        object_value = {}

        # Map each parameter to its corresponding value in the combination
        for param, value in zip(params, param_values):
            # if isinstance(value, dict):
            #     object_value[param] = generate_combinations(obj_name, value, increments)
            # elif isinstance(value, list):
            #     object_value[param] = [generate_values(v, increments[obj_name][param]) for v in value]
            # else:
            object_value[param] = value

        # Append the resulting dictionary to the list of value combinations
        value_combinations.append(object_value)

    return value_combinations

def generate_config_combinations(object_values):
    permutations = list(product(*object_values.values()))
    return [dict(zip(object_values.keys(), p)) for p in permutations]

def generate_object_combinations(parameter_ranges, increments):
    object_value_combos = {}
    for obj_name, params in parameter_ranges.items():
        # if isinstance(increments[obj_name].items(),int or float or list): # TODO: Add float check
        #     print("original structure")
        #     # parameter_value_combinations =  generate_parameter_value_combinations(obj_name, params, increments[obj_name])
        #     # object_value_combos[obj_name] =assign_value_names(parameter_value_combinations, params)
        # elif isinstance(increments[obj_name].items(),dict):
        #     print("Not a value going deeper into structure")
        # elif isinstance(increments[obj_name],int or float or list): # TODO: Add float check
        #     print("Reached values/")
        #     # parameter_value_combinations =  generate_parameter_value_combinations(obj_name, params, increments[obj_name])
        #     # object_value_combos[obj_name] =assign_value_names(parameter_value_combinations, params):
        # else:
        parameter_value_combinations =  generate_parameter_value_combinations(obj_name, params, increments)
        object_value_combos[obj_name] =assign_value_names(parameter_value_combinations, params)
            # print("Unknown structure")

    return generate_config_combinations(object_value_combos)

# Helper function to generate values
def generate_values_from_range(param, increment):
    min_value = param.get('min', 0)  # Default to 0 if 'min' is not present
    max_value = param.get('max', 0)  # Default to 0 if 'max' is not present
    current_value = min_value
    values = []
    while current_value <= max_value:
        values.append(current_value)
        current_value += increment
    return values




# # Example usage 1: Normal int/float values for nucleus generator:
# parameter_ranges_nucleus = {
#     'core': {'radius': {'min': 1.0, 'max': 3.0}},
#     'addon1': {'radius': {'min': 1.5, 'max':2.5}, 'length': {'min': 1.0, 'max': 3.0}}
# }
#
# increments_nucleus = {
#     'core': {'radius': 1.0},
#     'addon1': {'radius': 1.0, 'length': 1.0}
# }
#
# print("Simple nucleus parameter range testing:")
# combinations_nucleus = generate_object_combinations(parameter_ranges_nucleus, increments_nucleus)
# print("Combination of all objects within the range:")
# for combination in combinations_nucleus:
#     print(f"{combination}")


# Example usage 2: Normal int/float values and array handling for nucleus generator:

parameter_ranges_nucleus_array = {
    'core': {'radius': {'min': 1.0, 'max': 3.0}, 'rotation': [{'min': 1.0, 'max': 2.0}, {'min': 2.0, 'max': 3.0}, {'min': 2.0, 'max': 4.0}]},
    'addon1': {'radius': {'min': 1.5, 'max': 2.5}, 'length': {'min': 1.0, 'max': 3.0}}
}

increments_nucleus_array = {
    'core': {'radius': 1.0, 'rotation': [1.0, 1.0, 1.0]},
    'addon1': {'radius': 1.0, 'length': 1.0}
}

print("Array handling for nucleus parameter range testing:")
combinations_nucleus_array = generate_object_combinations(parameter_ranges_nucleus_array, increments_nucleus_array)
print("Combination of all objects within the range:")
for combination in combinations_nucleus_array:
    print(f"{combination}")

# # Example usage 3:  Normal values with other levels of nexted than core, for example animation:
# parameter_ranges_animation ={
#     "fps": {'min': 23, 'max': 25},
#     "2fps": {'min': 20, 'max': 23}
#     # "rotation_parameters": {
#     #     "B2_main_rotation": {
#     #         "period": {'min': 3, 'max': 5}
#     #     },
#     #     "B2_precession": {
#     #         "period": {'min': 90, 'max': 110}
#     #     }
#     # },
#     # "fly_by_parameters": {
#     #     "speed": {'min': 75, 'max': 85},
#     #     "t_start": {'min': -1230, 'max': -1110}
#     # }
# }
#
# increments_animation ={
#     "fps": 1,
#     "2fps": 0
#     # "rotation_parameters": {
#     #     "B2_main_rotation": {
#     #         "period": 1
#     #     },
#     #     "B2_precession": {
#     #         "period": 10
#     #     }
#     # },
#     # "fly_by_parameters": {
#     #     "speed": 5,
#     #     "t_start": 10
#     # }
# }
#
# print("Simple nucleus parameter range testing:")
# combinations_animation = generate_object_combinations(parameter_ranges_animation, increments_animation)
# print("Combination of all objects within the range:")
# for combination in combinations_animation:
#     print(f"{combination}")
