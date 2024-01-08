import json
import itertools
import numpy as np
from copy import deepcopy
from itertools import product

class JsonParameterUpdater:
    def __init__(self, target_file, parameter_range_file, parameter_increments_file):
        self.target_file = target_file
        self.parameter_range_file = parameter_range_file
        self.parameter_increments_file = parameter_increments_file

    @staticmethod
    def load_json(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def save_json(data, file_path):
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)

    def create_parameter_permutations(self):
        parameter_range = self.load_json(self.parameter_range_file)
        parameter_increments = self.load_json(self.parameter_increments_file)

        # Create all permutations of data based on range in parameter ranges and increments
        # permutations = self._generate_permutations(parameter_range, parameter_increments)
        permutations = self.generate_combinations(parameter_range, parameter_increments)

        # Run through all permutations, pass them to the recursive update
        print(f"All permutations: {permutations}")
        for permutation in permutations:
            print(f"Running permutation: {permutation}")
            # self._run_recursive_update(permutation)
        
        return permutations


    def generate_combinations(self, parameter_ranges, increments):
        # Get the parameter names (e.g., 'radius', 'length')
        parameter_names = set(parameter_ranges.keys())

        # Create a list to store all combinations
        combinations = []

        # Iterate through all combinations of values for each parameter
        for values in product(*[range(parameter_ranges[name]['min'], parameter_ranges[name]['max'] + 1, increments[name]) for name in parameter_names]):
            combination = {}
            for name, value in zip(parameter_names, values):
                combination[name] = value / 10.0  # Adjust for your specific case (e.g., divide by 10)
            combinations.append(combination)

        return combinations

    # Example usage:
    parameter_ranges = {
        'core': {'radius': {'min': 10, 'max': 40}, 'length': {'min': 20, 'max': 30}},
        'addon1': {'radius': {'min': 15, 'max': 25}, 'length': {'min': 10, 'max': 30}},
    }

    increments = {'core': {'radius': 5, 'length': 5}, 'addon1': {'radius': 5, 'length': 5}}

    combinations = generate_combinations(parameter_ranges, increments)
    print(combinations)


    def _generate_permutations(self, parameter_range, parameter_increment):
        core_parameters = parameter_range.get('cores', {})
        core_increment = parameter_increment.get('cores', {})
        print(f"core_parameters: {core_parameters}")
        print(f"core_increments: {core_increment}")

        # Generate permutations for each core
        core_permutations = self._generate_core_permutations(core_parameters, core_increment)

        # Construct parameter dictionaries for each permutation
        parameter_permutations = []
        for core_params in core_permutations:
            parameter_permutation = deepcopy(parameter_range)  # Make a deep copy of the parameter_range for each permutation
            parameter_permutation['cores'].update(core_params)
            parameter_permutations.append(parameter_permutation)

        return parameter_permutations

    def _generate_core_permutations(self, core_parameters, core_increment):
        parameter_names = core_parameters.keys()
        print(f"Parameter names: {parameter_names}")
        for name in parameter_names:
            print(f"Name: {name} Range: {core_parameters[name]}, Incremenet: {core_increment.get(name, 1)}")
        parameter_values = [self._generate_parameter_values(core_parameters[name], core_increment.get(name, 1)) for name in parameter_names]

        # Construct all possible permutations
        permutations = list(itertools.product(*parameter_values))

        # Create dictionaries for each permutation
        core_permutations = []
        for values in permutations:
            core_params = {name: value for name, value in zip(parameter_names, values)}
            core_permutations.append(core_params)

        return core_permutations

    def _generate_parameter_values(self, parameter_range, increment):
        print(f"")
        min_value = parameter_range.get('min')
        print(f"Minimum value: {min_value}")
        max_value = parameter_range.get('max')
        print(f"Maximum value: {max_value}")

        if isinstance(min_value, dict):
            min_value = min_value.get('default', 0.0)

        if isinstance(max_value, dict):
            max_value = max_value.get('default', 1.0)

        return list(
            float(value)
            for value in np.arange(min_value * 10, (max_value + increment) * 10, increment * 10)
        ) / 10.0



    def update_and_run_all_permutations(self, permutations, subprocess):
    
    
        self.target_data = self.load_json(self.target_file)
        # TODO: Run iterate through all permutations
        
        # Update the json for each permutations
        # Update the parameters based on permutations
        self._recursive_update(self.target_data, permutations)

        # Save the updated data back to the target JSON file
        self.save_json(self.target_data, self.target_file)
        print(f"New data: {self.target_data}")
        # TODO: Run each one subprocess at a time
        # TODO: No multi threading
    
    def update_and_run_all_permutations(self, permutations, subprocess_command):
        self.target_data = self.load_json(self.target_file)

        # Iterate through all permutations
        for i, params in enumerate(permutations, start=1):
            print(f"\nRunning process for permutation {i}:")
            print(json.dumps(params, indent=2))

            # Update the json for each permutation
            # Update the parameters based on permutations
            self._recursive_update(self.target_data, params)

            # Save the updated data back to the target JSON file
            self.save_json(self.target_data, self.target_file)
            print(f"Updated data: {self.target_data}")

            # Run the subprocess for each permutation
            self._run_subprocess(subprocess_command)

    def _recursive_update(self, target, source):
        """
        Recursively update target dictionary with non-dictionary values from the source.
        """
        for key, value in source.items():
            if isinstance(value, dict):
                # If the value is a dictionary, recursively update
                target[key] = self._recursive_update(target.get(key, {}), value)
        # FEATURE: Add warning when the updater json provides a parameter
            else:
                # If the value is not a dictionary, update directly
                target[key] = value

        return target
    def _run_subprocess(self, subprocess_command):
        # Implement your subprocess execution logic here
        # For example, run a subprocess with the updated parameters
        # You can customize this part based on your specific use case
        print("Running subprocess with updated parameters:", self.target_data)
        # Example: subprocess.run(['your_command_here', '--file', self.target_file])

if __name__ == "__main__":
    # Create instances of JsonParameterUpdater for each file type
    # updater_1 = JsonParameterUpdater('src/utils/nucleus.json', 'src/utils/nucleus_parameter_ranges.json','src/utils/nucleus_increments.json')
    updater_1 = JsonParameterUpdater('nucleus.json', 'nucleus_parameter_ranges.json','nucleus_increments.json')
    # updater_2 = JsonParameterUpdater('dustjet.json', 'dustjet_increments.json')

    # Call the update_parameters method for each instance
    permutations = updater_1.create_parameter_permutations()
    updater_1.update_and_run_all_permutations(permutations, "test")
    # updater_1.update_parameters()
    # updater_2.update_parameters()

    updater_1._run_subprocess()

