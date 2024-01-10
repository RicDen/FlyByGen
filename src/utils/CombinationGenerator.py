from itertools import product

def generate_value_combination(parameter_ranges, increments):
    # Get the parameter names (e.g., 'radius', 'length')
    object_names = list(parameter_ranges.keys())
    # Create a list to store all combinations
    object_value_combos = {}

    # Create combinations for all parameters of each object

    for obj_name in object_names:
        value_combinations = []
        parameter_names = list(parameter_ranges[obj_name].keys())
        parameter_combinations = product(*[generate_values(parameter_ranges[obj_name][param]['min'],
                                                           parameter_ranges[obj_name][param]['max'],
                                                           increments[obj_name][param]) for param in parameter_names])

        for index, param_values in enumerate(parameter_combinations):
            object_value = {}
            for param, value in zip(parameter_names, param_values):
                object_value[param] = value
            # index_obj_name = f"{obj_name}_{index}"
            value_combinations.append(object_value)
        object_value_combos[obj_name] = value_combinations
    return object_value_combos

def generate_object_combinations(object_values):
    permutations = list(product(*object_values.values()))
    return [dict(zip(object_values.keys(), p)) for p in permutations]


    #
    # for obj_name, values in object_values.items():
    #     combined_objects = {}
    #     for core_comb in core_combinations:
    #         for addon_comb in addon_combinations:
    #
    #             combined_key = f"{core_comb}, {addon_comb}"
    #             core_values = object_value_combinations[core_comb]
    #             addon_values = object_value_combinations[addon_comb]
    #             combined_value = {}
    #             combined_value[core_comb] = core_values
    #             combined_value[addon_comb] = addon_values
    #             combined_objects[combined_key] = combined_value
    #
    # return combined_objects

# Helper function to generate floating-point values
def generate_values(min_value, max_value, increment):
    current_value = min_value
    while current_value <= max_value:
        yield current_value
        current_value += increment

# Example usage: Normal int/float values for nucleus generator:
parameter_ranges_nucleus = {
    'core': {'radius': {'min': 1.0, 'max': 3.0}, 'length': {'min': 1.0, 'max': 2.0}},
    'addon1': {'radius': {'min': 1.5, 'max':2.5}, 'length': {'min': 1.0, 'max': 3.0}},
    'addon2': {'radius': {'min': 1.5, 'max':2.5}, 'length': {'min': 1.0, 'max': 3.0}}
}

increments_nucleus = {
                'core': {'radius': 1.0, 'length': 1.0},
                'addon1': {'radius': 1.0, 'length': 1.0},
                'addon2': {'radius': 1.0, 'length': 1.0}
              }

print("Simple nucleus parameter range testing:")
value_combinations_nucleus = generate_value_combination(parameter_ranges_nucleus, increments_nucleus)
print("Combination of each object:")
for combination in value_combinations_nucleus:
    print(f"{combination}: {value_combinations_nucleus[combination]}")
combinations_nucleus = generate_object_combinations(value_combinations_nucleus)
print("Combination of all objects within the range:")
for combination in combinations_nucleus:
    print(f"{combination}")

# # Example usage 2:  Normal values with other levels of nexted than core, for example animation:
# parameter_ranges_animation ={
#         "rotation_parameters": {
#         "B2_main_rotation": {
#             "period": {'min': 3, 'max': 5}
#         },
#         "B2_precession": {
#             "period": {'min': 90, 'max': 110}
#         }
#     },
#         "fly_by_parameters": {
#         "speed": {'min': 75, 'max': 85},
#         "t_start": {'min': -1230, 'max': -1110}
#         },
#         "fps": {'min': 23, 'max': 25}
#     }
#
# increments_animation ={
#         "rotation_parameters": {
#         "B2_main_rotation": {
#             "period": 1
#         },
#         "B2_precession": {
#             "period": 10
#         }
#     },
#         "fly_by_parameters": {
#         "speed": 5,
#         "t_start": 10
#         },
#         "fps": 1
#     }
#
# # print("Animation parameter range testing:")
# # value_combinations_animation = generate_value_combination(parameter_ranges_animation, increments_animation)
# # # combinations_animation = generate_object_combinations(value_combinations_animation)
# # for combination in value_combinations_animation:
# #     print(f"{combination}: {value_combinations_animation[combination]}")
