from itertools import product
import logging
class ParameterCombinationGenerator:
    def __init__(self):
        logging.info("Creating all combination according to parameter range and increments...")

    
    def generate_value_combo_list(self, params, increments):
        """
        Generate a list of value combinations based on the given parameters and increments.

        Args:
            params (dict): A dictionary containing the parameters and their values.
            increments (dict): A dictionary containing the increments for each parameter.

        Returns:
            list: A list of value combinations.

        Raises:
            ValueError: If the parameters or increments are invalid.

        """
        generated_values = []
        for param in params:
            if isinstance(increments[param], float) or isinstance(increments[param], int):
                generated_values.append(self.generate_values_from_range(params[param], increments[param]))
            elif isinstance(params[param], list):
                logging.info("Vector in form of list provided")
                vector = []
                for (i, value) in enumerate(params[param]):
                    vector.append(self.generate_values_from_range(value, increments[param][i]))
                permutations = [list(perm) for perm in product(*vector)]
                generated_values.append(permutations)
            else:
                logging.info("Error: Invalid parameters")
        return product(*generated_values)

    def assign_value_names(self, parameter_combinations, params):
            """
            Assigns value names to parameter combinations.

            Args:
                parameter_combinations (list): List of parameter combinations.
                params (list): List of parameter names.

            Returns:
                list: List of dictionaries representing value combinations.
            """
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

    def generate_config_combinations(self, object_values):
        """
        Generate all possible combinations of object values.

        Args:
            object_values (dict): A dictionary containing the object values.

        Returns:
            list: A list of dictionaries representing the combinations.

        """
        permutations = list(product(*object_values.values()))
        return [dict(zip(object_values.keys(), p)) for p in permutations]


    def generate_parameter_combinations(self, parameter_ranges, increments):
        """
        Generate all possible combinations of parameter values based on the given ranges and increments.

        Args:
            parameter_ranges (dict): A dictionary containing the parameter ranges.
            increments (dict): A dictionary containing the increments for each parameter.

        Returns:
            list: A list of dictionaries representing the combinations.

        """
        combo_dict = {}
        first_layer_entries = {}
        first_layer_entries["range"] = {}
        first_layer_entries["increments"] = {}
        recursion = False
        parameter = False
        # Iterate over each parameter and its increment value
        for key, value in increments.items():
            # If the increment value is a dictionary, it means there is a nested parameter
            if isinstance(value, dict):
                recursion = True
                # Recursively generate combinations for the nested parameter
                combo_dict[key] = self.generate_parameter_combinations(parameter_ranges[key], increments[key])
            else:
                parameter = True
                # Store the range and increment values for the first layer parameters
                first_layer_entries["range"][key] = parameter_ranges[key]
                first_layer_entries["increments"][key] = increments[key]

        # If there are nested parameters, generate combinations for them
        if recursion:
            recursive_list = self.generate_config_combinations(combo_dict)

        # If there are first layer parameters, generate combinations for them
        if parameter:
            # Check if the parameter ranges are different from the first layer entries
            if parameter_ranges != first_layer_entries["range"]:
                print("Creating first layer combos")
                # Generate value combinations for the first layer parameters
                first_layer_parameter_value_combinations = self.generate_value_combo_list(first_layer_entries["range"], first_layer_entries["increments"])
                # Assign value names to the first layer parameter combinations
                first_layer_combo_list = self.assign_value_names(first_layer_parameter_value_combinations, first_layer_entries["range"])
                # Combine the first layer parameter combinations with the recursive combinations
                recursive_list = [{**dict1, **dict2} for dict1, dict2 in product(first_layer_combo_list, recursive_list)]

            # If there are no nested parameters, generate combinations for the first layer parameters
            if len(combo_dict) == 0:
                # Generate value combinations for the first layer parameters
                recursive_parameter_value_combinations = self.generate_value_combo_list(parameter_ranges, increments)
                # Assign value names to the first layer parameter combinations
                recursive_list = self.assign_value_names(recursive_parameter_value_combinations, parameter_ranges)

        return recursive_list
        
        def generate_values_from_range(self, param, increment):
            """
            Generate a list of values from a given range and increment.

            Args:
                param (dict): A dictionary containing the range of values.
                increment (float): The increment value.

            Returns:
                list: A list of values.

            """
            # Get the minimum and maximum values from the range
            min_value = param.get('min', 0)
            max_value = param.get('max', 0)
            current_value = min_value
            values = []
            # Generate values within the range
            while current_value <= max_value:
                values.append(current_value)
                # If the current value is a dictionary, stop generating values
                if isinstance(current_value, dict):
                    break
                else:
                    # Increment the current value
                    current_value += increment
            return values




# Test cases for example dictionaries
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

# # Example usage 3:  Normal values with other levels of nexted than core, for example animation:
# parameter_ranges_animation ={
#     "fps": {'min': 22, 'max': 25},
#     "rotation_parameters": {
#         "B2_main_rotation": {
#             "period": {'min': 3, 'max': 5}
#         }
#     },
#     "fly_by_parameters": {
#         "speed": {'min': 75, 'max': 85},
#         "t_start": {'min': -1230, 'max': -1110}
#     }
# }
#
# increments_animation ={
#     "fps": 1,
#     "rotation_parameters": {
#         "B2_main_rotation": {
#             "period": 1
#         }
#     },
#     "fly_by_parameters": {
#         "speed": 5,
#         "t_start": 10
#     }
# }
#
# print("Simple nucleus parameter range testing:")
# combinations_animation = generate_parameter_combinations(parameter_ranges_animation, increments_animation)
# print("Combination of all objects within the range:")
# for combination in combinations_animation:
#     print(f"{combination}")
