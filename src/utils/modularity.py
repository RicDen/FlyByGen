
import importlib.util
import sys
import json
with open('src/config/paths.json', 'r') as f:
    paths = json.load(f)
sys.path.append(paths['project_directory'])

class ModuleManager:
    def __init__(self, class_path, module_name, class_name):
        self.class_path = class_path
        self.module_name = module_name
        self.class_name = class_name
        self.module = None
        self.instance = None

    def import_and_instantiate_class(self):
        module_spec = importlib.util.spec_from_file_location(f"module.{self.module_name}", self.class_path)
        self.module = importlib.util.module_from_spec(module_spec)
        sys.modules[f"module.{self.module_name}"] = self.module
        module_spec.loader.exec_module(self.module)

        if hasattr(self.module, self.class_name):
            class_ = getattr(self.module, self.class_name)
            self.instance = class_()
        else:
            raise AttributeError(f"Class '{self.class_name}' not found in module '{self.module_name}'")

    def get_instance(self):
        if self.instance is None:
            self.import_and_instantiate_class()
        return self.instance
    