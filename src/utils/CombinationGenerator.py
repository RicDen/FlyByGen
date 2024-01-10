from itertools import product

def generate_value_combination(parameter_ranges, increments):
    object_value_combos = {}

    def generate_combinations(obj_name, params, increments):
        value_combinations = []
        generated_values = []
        for param in params:
            if isinstance(params[param], dict ):
                generated_values.append(generate_values(params[param], increments[obj_name][param]))
            elif isinstance(params[param], list):
                print("Vector in form of list provided")
                vector = []
                for (i, value) in enumerate(params[param]):
                    vector.append(generate_values(value, increments[obj_name][param][i]))
                # permutations = list(product(*vector))
                permutations = [list(perm) for perm in product(*vector)]
                generated_values.append(permutations)
                # and created all list option

            else:
                print("Error: Invalid parameters")
        parameter_combinations = product(*generated_values)
        # parameter_combinations = product(
        #     *[generate_values(params[param], increments[obj_name][param]) for param in params])

        for param_values in parameter_combinations:
            object_value = {}
            for param, value in zip(params, param_values):
                # if isinstance(value, dict):
                #     object_value[param] = generate_combinations(obj_name, value, increments)
                # elif isinstance(value, list):
                #     object_value[param] = [generate_values(v, increments[obj_name][param]) for v in value]
                # else:
                object_value[param] = value
            value_combinations.append(object_value)
        return value_combinations

    for obj_name, params in parameter_ranges.items():
        object_value_combos[obj_name] = generate_combinations(obj_name, params, increments)

    return object_value_combos

def generate_object_combinations(object_values):
    permutations = list(product(*object_values.values()))
    return [dict(zip(object_values.keys(), p)) for p in permutations]

# Helper function to generate values
def generate_values(param, increment):

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
# value_combinations_nucleus = generate_value_combination(parameter_ranges_nucleus, increments_nucleus)
# print("Combination of each object:")
# for combination in value_combinations_nucleus:
#     print(f"{combination}: {value_combinations_nucleus[combination]}")
# combinations_nucleus = generate_object_combinations(value_combinations_nucleus)
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
value_combinations_nucleus_array = generate_value_combination(parameter_ranges_nucleus_array, increments_nucleus_array)
print("Combination of each object:")
for combination in value_combinations_nucleus_array:
    print(f"{combination}: {value_combinations_nucleus_array[combination]}")
combinations_nucleus_array = generate_object_combinations(value_combinations_nucleus_array)
print("Combination of all objects within the range:")
for combination in combinations_nucleus_array:
    print(f"{combination}")

# # Example usage 3:  Normal values with other levels of nexted than core, for example animation:
# parameter_ranges_animation ={
#     "rotation_parameters": {
#         "B2_main_rotation": {
#             "period": {'min': 3, 'max': 5}
#         },
#         "B2_precession": {
#             "period": {'min': 90, 'max': 110}
#         }
#     },
#     "fly_by_parameters": {
#         "speed": {'min': 75, 'max': 85},
#         "t_start": {'min': -1230, 'max': -1110}
#     },
#     "fps": {'min': 23, 'max': 25}
# }
#
# increments_animation ={
#     "rotation_parameters": {
#         "B2_main_rotation": {
#             "period": 1
#         },
#         "B2_precession": {
#             "period": 10
#         }
#     },
#     "fly_by_parameters": {
#         "speed": 5,
#         "t_start": 10
#     },
#     "fps": 1
# }
#
# print("Simple nucleus parameter range testing:")
# value_combinations_animation = generate_value_combination(parameter_ranges_animation, increments_animation)
# print("Combination of each object:")
# for combination in value_combinations_animation:
#     print(f"{combination}: {value_combinations_animation[combination]}")
# combinations_animation = generate_object_combinations(value_combinations_animation)
# print("Combination of all objects within the range:")
# for combination in combinations_animation:
#     print(f"{combination}")
