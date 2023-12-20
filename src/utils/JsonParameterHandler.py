import json
import random
from copy import deepcopy

class JsonFileHandler:
    @staticmethod
    def load_json(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def save_json(data, file_path):
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)

class JsonParameterUpdater:
    def __init__(self, target_path, range_path, increment_path=None):
        self.target_path = target_path
        self.range_path = range_path
        self.increment_path = increment_path

    def update_parameters(self):
        # Load the target JSON file
        target_data = JsonFileHandler.load_json(self.target_path)

        # Load the parameter range JSON files for cores and addons
        range_data = JsonFileHandler.load_json(self.range_path)
        increment_data = JsonFileHandler.load_json(self.increment_path) if self.increment_path else None

        # Update parameters based on the provided ranges and increments
        for core in target_data['cores']:
            self._update_category_parameters(core, range_data['cores'], increment_data['cores'])

        # for addon in target_data['addons']:
        #     self._update_category_parameters(addon, range_data['addons'], increment_data['addons'])
        print(f"Target data is: {target_data}")
        # Save the updated data back to the target JSON file
        JsonFileHandler.save_json(target_data, self.target_path)

    def _update_category_parameters(self, category_data, range_data, increment_data):
        for parameter_name, parameter_range in range_data.items():
            if parameter_name in category_data:
                increment = increment_data.get(parameter_name, 1) if increment_data else 1
                current_value = category_data[parameter_name]

                if isinstance(current_value, list):
                    new_value = [v + increment for v in current_value]
                    new_value = [max(min(v, parameter_range['max']), parameter_range['min']) for v in new_value]
                else:
                    new_value = current_value + increment
                    new_value = max(min(new_value, parameter_range['max']), parameter_range['min'])

                category_data[parameter_name] = new_value

if __name__ == "__main__":
    # Example usage
    target_path = 'nucleus.json'
    range_path = 'parameter_ranges.json'
    increment_path = 'increments.json'

    # Create an instance of JsonParameterUpdater
    updater = JsonParameterUpdater(target_path, range_path, increment_path)

    # Update the target JSON file iteratively based on parameter ranges and increments
    updater.update_parameters()

    print(f"Updated {target_path} iteratively based on {range_path} and {increment_path}")
