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

    return object_values

# Helper function to generate floating-point values
def generate_values(min_value, max_value, increment):
    current_value = min_value
    while current_value <= max_value:
        yield current_value
        current_value += increment

# Example usage:
parameter_ranges = {
    'core': {'radius': {'min': 1.0, 'max': 3.0}, 'length': {'min': 2.0, 'max': 3.0}},
    'addon1': {'radius': {'min': 1.5, 'max': 2.5}, 'length': {'min': 1.0, 'max': 3.0}},
}

increments = {'core': {'radius': 1.0, 'length': 1.0}, 'addon1': {'radius': 1.0, 'length': 1.0}}

combinations = generate_object_values(parameter_ranges, increments)
for combination in combinations:
    print(f"{combination}{combinations[combination]}")
