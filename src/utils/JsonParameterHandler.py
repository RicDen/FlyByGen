import json
import logging
import os

from src.utils.ParameterCombinationGenerator import ParameterCombinationGenerator

with open('src/config/paths.json', 'r') as f:
    paths = json.load(f)

    class JsonParameterUpdater:
        def __init__(self, target_file, parameter_range_file, increments_file, OutputLogging):
            """
            Initialize the JsonParameterUpdater class.

            Args:
                target_file (str): The path to the target JSON file.
                parameter_range_file (str): The path to the parameter range JSON file.
                increments_file (str): The path to the increments JSON file.
                OutputLogging (object): The OutputLogging object for logging.
            """
            self.target_file = target_file
            self.parameter_range_file = parameter_range_file
            self.increments_file = increments_file
            self.OutputLogging = OutputLogging

        def create_parameter_combinations(self):
            """
            Create parameter combinations based on the target, parameter range, and increments files.

            Returns:
                tuple: A tuple containing the adjustment data and target data.
            """
            # Load the JSON data from the files
            with open(self.target_file, 'r') as file:
                self.target_data = json.load(file)

            with open(self.parameter_range_file, 'r') as file:
                parameter_range_data = json.load(file)

            with open(self.increments_file, 'r') as file:
                increments_data = json.load(file)
            logging.info(f"Opened Config range, increment and target file.")
            ParamCombiner = ParameterCombinationGenerator()
            self.adjustment_data = ParamCombiner.generate_parameter_combinations(parameter_range_data, increments_data)
            logging.info(f"Created all configurations combinations.")
            return self.adjustment_data, self.target_data

        def run_parameter_combinations(self, adjustment_data, target_data, cmd):
            """
            Run parameter combinations and update the target JSON file.

            Args:
                adjustment_data (list): The list of adjustment data.
                target_data (dict): The target data.
                cmd (str): The command to run for each combination.

            """
            # Update the parameters based on adjustments
            for i, update in enumerate(adjustment_data):
                logging.info(f"Running combination {i+1} out of {len(adjustment_data)}")
                logging.info(f"Values are: {update}")
                self._recursive_update(target_data, update)
                # Save the updated data back to the target JSON file
                with open(self.target_file, 'w') as file:
                    json.dump(target_data, file, indent=2)
                    logging.info(f"Updated target file with new values: {target_data}")
                
                logging.info(f"Original paths file: {paths}")
                for key, value in paths.items():
                    if key == "combination":
                        # If the value is a dictionary, recursively update
                        logging.info("Combination key found, updating value")
                        paths[key] = f"comb_{i}"
                    # FEATURE: Add warning when the updater json provides a parameter

                with open('src/config/paths.json', 'w') as file:
                    json.dump(paths, file, indent=2)
                    logging.info(f"Updated paths file: {paths}")
                meta_param_path = os.path.join((paths["dataset_cache"] + paths["pipeline_version"] + paths["number_of_generation"]), paths["combination"])
                os.makedirs(meta_param_path, exist_ok=True)
                meta_param_file = os.path.join(meta_param_path, "meta_param.json")
                with open(meta_param_file, 'w') as file:
                    json.dump(target_data, file, indent=2)
                    logging.info(f"Saved parameter meta to file: {meta_param_file}")

                self.OutputLogging.run_subprocess(cmd)
            logging.info(f"Finished running all combinations")

        def _recursive_update(self, target, source):
            """
            Recursively update target dictionary with non-dictionary values from the source.

            Args:
                target (dict): The target dictionary to update.
                source (dict): The source dictionary to update from.

            Returns:
                dict: The updated target dictionary.
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

# if __name__ == "__main__":
#     # Create instances of JsonParameterUpdater for each file type
#     updater_1 = JsonParameterUpdater('nucleus.json', '../config/blender/nucleus_parameter_ranges.json',
#                                      '../config/blender/nucleus_increments.json')
#     # updater_2 = JsonParameterUpdater('dustjet.json', 'dustjet_increments.json')
#
#     # Call the update_parameters method for each instance
#     updater_1.create_parameter_combinations()
#     updater_1.run_parameter_combinations(updater_1.adjustment_data, updater_1.target_data)
#     # updater_2.update_parameters()
