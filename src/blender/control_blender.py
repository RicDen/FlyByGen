'''
Run the full workflow
Include setting up of scene, adapting parameters, rendering and deleting of scene for next generation.
Tasks:
'''
# TODO: Update architecture

# FEATURE: Create way to create fundamental base script with all materials included
import bpy
import os
import json
import sys
import time
import logging
with open('src/config/paths.json', 'r') as f:
    paths = json.load(f)
sys.path.append(paths['project_directory'])
from src.utils.modularity import ModuleManager


class BlenderControl:
    # FEATURE: Add automatically incremented blender file name if file exists
# FEATURE: Modularise python library import
    def setup_check(self):
        try:
            import psutil
            logging.info(f"Loaded python libraries loaded successfully")
        except:
            logging.error(f"Failed to load. Installing python libraries...")
            import pip
            print(pip.main(['install', 'psutil']))
            import psutil
            logging.warning(f"Loaded modules after install.")
    

    def save_blender_project(self, cache, pipeline_version, number_of_generation, filename):
        """

        .. _saveblenderproject:

        Function to save the blender project after each module is run.

        Included functionalities are:
        
        - Creation of according directory as specified in paths.json
        - Try and catch of project saving errors

        :param cache: Specifies the cache path

        :param pipeline_version: Specifies the version of the pipeline to define specific configurations
        
        :param number_of_generation: Data generation run. This number shall be updated automatically when the pipeline is completed

        :param filename: Name of the save file
        """
        try:
            # Specify the path of the new directory
            project_dir = os.path.join(
                cache, f"{pipeline_version}{number_of_generation}")
            # Create the new directory if it doesn't exist
            if not os.path.exists(project_dir):
                os.makedirs(project_dir)
                logging.info(f"Created new directory: {project_dir}")
            else:
                logging.warning("Folder already exists, no new folder created")

            # Specify the file path
            blender_file_path = os.path.join(project_dir, filename + ".blend")
            logging.info("Saving scene to: " + blender_file_path)

            # Convert the filepath to an absolute path
            abs_filepath = os.path.abspath(blender_file_path)

            # Save the blend file
            bpy.ops.wm.save_as_mainfile(filepath=abs_filepath)
            logging.info("Blend file saved successfully")
        except OSError as e:
            logging.error(f"Error occurred while saving blender file: {e}")
        except Exception as e:
            logging.error(
                f"An error occurred while saving the blend file: {e}")

    def run_blender_modules(self, blender_modules):
        """
        This function runs all the previously loaded modules according to the parameters specified for each of the modules.
        A time measurement is included to allow estimates of the project run times if a larger amount of data is being created.
        Each of the project modules will be saved with the :func:`save_blender_project()`.

        :param blender_modules: Loaded modules specified by path as well as module and class name

        :return: Instances of each module will be returned, so they can be referenced to at a later point if needed

        :rtype: module instance
        """
        start_time = time.time()
        instances = []
        for module in blender_modules["modules"]:
            class_path = module["class_path"]
            module_name = module["module_name"]
            class_name = module["class_name"]
            # TODO: Each module shall have a start and finish message
            single_module = ModuleManager(class_path, module_name, class_name)
            module_instance = single_module.get_instance()
            logging.info(f"Loaded: {module_name}")
            self.save_blender_project(paths['cache_dir'], paths['pipeline_version'],
                                 paths['number_of_generation'], module_name)
            instances.append(module_instance)
        end_time = time.time()
        logging.info(f"Generation took {end_time-start_time}s")
        return instances


    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.setup_check()
        with open(paths["blender_modules_path"]) as modules_specs:
            specs = json.load(modules_specs)
        instances = self.run_blender_modules(specs)
        logging.info("Finished blender control")

BlenderControl()