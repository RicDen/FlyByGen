import json

class JsonParameterUpdater:
    def __init__(self, target_file, adjustment_file):
        self.target_file = target_file
        self.adjustment_file = adjustment_file

    def update_parameters(self):
        # Load the JSON data from the files
        with open(self.target_file, 'r') as file:
            target_data = json.load(file)

        with open(self.adjustment_file, 'r') as file:
            adjustment_data = json.load(file)

        # Update the parameters based on adjustments
        self._recursive_update(target_data, adjustment_data)

        # Save the updated data back to the target JSON file
        with open(self.target_file, 'w') as file:
            json.dump(target_data, file, indent=2)

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
    updater_1 = JsonParameterUpdater('nucleus.json', 'nucleus_increments.json')
    updater_2 = JsonParameterUpdater('dustjet.json', 'dustjet_increments.json')

    # Call the update_parameters method for each instance
    updater_1.update_parameters()
    updater_2.update_parameters()
