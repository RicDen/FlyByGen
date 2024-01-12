import json
import time

from src.utils.ParameterCombinationGenerator import ParameterCombinationGenerator

class JsonParameterUpdater:
    def __init__(self, target_file, parameter_range_file, increments_file):
        self.target_file = target_file
        self.parameter_range_file = parameter_range_file
        self.increments_file = increments_file

    def create_parameter_combinations(self):
        # Load the JSON data from the files
        with open(self.target_file, 'r') as file:
            self.target_data = json.load(file)

        with open(self.parameter_range_file, 'r') as file:
            parameter_range_data = json.load(file)

        with open(self.increments_file, 'r') as file:
            increments_data = json.load(file)
        ParamCombiner = ParameterCombinationGenerator()
        self.adjustment_data = ParamCombiner.generate_parameter_combinations(parameter_range_data, increments_data)
        return self.adjustment_data, self.target_data
    def run_parameter_combinations(self, adjustment_data, target_data):
        # Update the parameters based on adjustments
        for i,update in enumerate(adjustment_data):
            print(f"Running combination {i+1} out of {len(adjustment_data)}")
            print(f"Values are: {update}")
            self._recursive_update(target_data, update)
            # Save the updated data back to the target JSON file
            with open(self.target_file, 'w') as file:
                json.dump(target_data, file, indent=2)
            # Simulate processing
            time.sleep(5)
        print(f"Finished running all combinations")


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

if __name__ == "__main__":
    # Create instances of JsonParameterUpdater for each file type
    updater_1 = JsonParameterUpdater('nucleus.json', 'nucleus_parameter_ranges.json', 'nucleus_increments.json')
    # updater_2 = JsonParameterUpdater('dustjet.json', 'dustjet_increments.json')

    # Call the update_parameters method for each instance
    updater_1.create_parameter_combinations()
    updater_1.run_parameter_combinations(updater_1.adjustment_data, updater_1.target_data)
    # updater_2.update_parameters()
