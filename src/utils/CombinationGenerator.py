from itertools import product

def generate_object_values(parameter_ranges, increments):
    # Get the parameter names (e.g., 'radius', 'length')
    object_names = list(parameter_ranges.keys())
    # Create a list to store all combinations
    object_values = {}

    # Create combinations for all parameters of each object

    for obj_name in object_names:
        parameter_names = list(parameter_ranges[obj_name].keys())
        parameter_combinations = product(*[generate_values(parameter_ranges[obj_name][param]['min'],
                                                           parameter_ranges[obj_name][param]['max'],
                                                           increments[obj_name][param]) for param in parameter_names])

        for index, param_values in enumerate(parameter_combinations):
            object_value = {}
            for param, value in zip(parameter_names, param_values):
                object_value[param] = value
            index_obj_name = f"{obj_name}_{index}"
            object_values[index_obj_name] = object_value

    # Create combinations of cores with addons
    core_combinations = [key for key in object_values.keys() if key.startswith('core')]
    addon_combinations = [key for key in object_values.keys() if key.startswith('addon')]

    combined_values = {}
    for core_comb in core_combinations:
        for addon_comb in addon_combinations:

            combined_key = f"{core_comb}, {addon_comb}"
            core_values = object_values[core_comb]
            addon_values = object_values[addon_comb]
            combined_value = {}
            combined_value[core_comb] = core_values
            combined_value[addon_comb] = addon_values
            combined_values[combined_key] = combined_value

    return combined_values

# Helper function to generate floating-point values
def generate_values(min_value, max_value, increment):
    current_value = min_value
    while current_value <= max_value:
        yield current_value
        current_value += increment

# Example usage:
parameter_ranges = {
    'core': {'radius': {'min': 1.0, 'max': 3.0}, 'length': {'min': 1.0, 'max': 2.0}},
    'addon1': {'radius': {'min': 1.5, 'max':2.5}, 'length': {'min': 1.0, 'max': 3.0}},
}

increments = {'core': {'radius': 1.0, 'length': 1.0}, 'addon1': {'radius': 1.0, 'length': 1.0}}

#
# parameter_ranges = {
#     'core': {'radius': {'min': 1.0, 'max': 3.0}, 'length': {'min': 1.0, 'max': 3.0}, 'rotation': [{'min': 1.0, 'max': 3.0},{'min': 2.0, 'max': 3.0}, {'min': 2.0, 'max': 4.0}]},
#     'addon1': {'radius': {'min': 1.5, 'max': 4.5}, 'length': {'min': 1.0, 'max': 3.0}},
# }
#
# increments = {'core': {'radius': 1.0, 'length': 1.0, 'rotation':[1,1,1]}, 'addon1': {'radius': 1.0, 'length': 1.0}}

combinations = generate_object_values(parameter_ranges, increments)
for combination in combinations:
    print(f"{combination}: {combinations[combination]}")
