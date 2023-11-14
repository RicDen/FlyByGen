import json
import sys    
import logging
import time
with open('src/config/paths.json', 'r') as f:
    paths = json.load(f)
sys.path.append(paths['project_directory'])
from src.utils.modularity import ModuleManager
   
class PostProcessor:
    def run_post_modules(self, blender_modules):
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
            instances.append(module_instance)
            module_time = time.time()
            logging.info(f"Module execution took {module_time-start_time}s")
        end_time = time.time()
        logging.info(f"Generation took {end_time-start_time}s")
        return instances
    
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        logging.info("Starting Post processing")
        with open(paths["post_modules_path"]) as modules_specs:
            specs = json.load(modules_specs)
        instances = self.run_post_modules(specs)
        logging.info("Finished Post processing control")

PostProcessor()