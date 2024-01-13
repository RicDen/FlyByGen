import bpy
import numpy as np
import sys
import json
import logging
import os
import subprocess
import time
# from src.utils.OutputLogger import OutputLogger

with open('src/config/paths.json', 'r') as f:
    paths = json.load(f)

sys.path.append(paths['project_directory'])



class DatasetGenerator:
    """
    This class creates the dataset of a defined scene from the currently opened blender file.
    The result will be rendered frames from all images with all the render layers defined in 
    the json file render.json.
    """
    def __init__(self) -> None:
        # Output directory for saving the images

        with open(paths['render_configs']) as json_file:
            parameters = json.load(json_file)
        output_dir = paths['dataset_cache']
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        self.config_image_for_dataset(parameters["image_settings"])

        # Render the scene and save the images
        self.render_scene(output_dir, parameters)

    def config_image_for_dataset(self, image_settings):
        """
        Sets the rendering settings for the scene from the dictionary given
        
        Parameters:
            image_settings (dict): A dictionary containing the image settings for the render.
        
        Example of image_settings dictionary:

        .. code-block:: text

            image_settings = {
                "file_format": "PNG",
                "color_mode": "RGBA",
                "color_depth": 16,
                "use_compositing": false,
                "use_pass_object_index": true
            }

        """
        scene = bpy.context.scene
        scene.render.image_settings.file_format = image_settings["file_format"]
        scene.render.image_settings.color_mode = image_settings["color_mode"]
        scene.render.image_settings.color_depth = image_settings["color_depth"]
        scene.render.use_compositing = image_settings["use_compositing"]
        scene.view_layers["ViewLayer"].use_pass_object_index = image_settings["use_pass_object_index"]

    def render_scene(self, output_dir, parameters):
        """
        Renders the entire project with every set frame of the animation and saves it all in a folder
        according to scene id given.
        Each frame will be rendered according to the layers specified. The layers will be selected by
        :func:```set_rendered_objects(self, material)```.
        
        Parameters:
            parameters (dict): A dictionary containing the data on the scene, 
            start and end frame, and the render layers.
        
        Example of image_settings dictionary:
        
        .. code-block:: text

            parameters = {
                "scene": "002",
                "start_frame": 500,
                "end_frame" :486,
                "render_layers":{
                    "nucleus":"AsteroidSurface.001",
                    "jets": "Dust.001",
                    "all": "all"
                    }
                }

        """
        # Set the output directory for saving images
        scene_id = paths["dataset_scene"]
        start_frame = parameters["start_frame"]
        end_frame = parameters["end_frame"]
        render_layers = parameters["render_layers"]
        if end_frame < start_frame:
            logging.error(f"Start frame number must be smaller than end frame number!"+
                      "Check the render.json for the correct definition")

        gpu_memory_threshold = sum(self.get_gpu_memory_total())
        gpu_memory = gpu_memory_threshold
        logging.info(f"GPU memory available: {gpu_memory}")
        # Set parameters from Json
        threshold_factor = 2.0
        load_delay = 4
        processes = []
        for frame in range(start_frame, end_frame + 1):
            logging.info(f"Rendering frame: {frame}...")
            for layer, object_name in render_layers.items():
                logging.info(f"Rendering layer: {layer}...")
                frame_output_path = os.path.join(
                    output_dir, f"{scene_id}", f"{layer}", f"frame_")
                logging.info(f"Frame Output path: {frame_output_path}")
                while True:
                    time.sleep(load_delay)
                    video_ram = self.get_gpu_memory_usage()
                    logging.info(f"Memory utilization: {video_ram}")  
                    if video_ram and all(mem < gpu_memory_threshold for mem in video_ram):
                        # GPU memory is below the threshold, start rendering
                        frame_process = self.render_frame(object_name, frame, frame_output_path)
                        if gpu_memory_threshold == gpu_memory:
                            logging.info(f"Setting GPU memory threshold...")
                            max_gpu_memory_usage = self.get_max_gpu_memory_usage(10)
                            logging.info(f"Maximum GPU usage is: {max_gpu_memory_usage}")
                            gpu_memory_threshold = gpu_memory - (max_gpu_memory_usage * threshold_factor)
                            logging.info(f"GPU memory threshold set to: {gpu_memory_threshold}")
                        break
                    
                    logging.warning("Waiting for GPU memory to become available...")
                                      
                processes.append(frame_process)
                logging.info(f"There are {len(processes)} running.")
            
        for process in processes:
            process.wait()
            

# TODO: Add path from json
    def render_frame(self, layer, frame, output_path):
        render_command = [
            "C:\\Program Files\\Blender Foundation\\Blender 3.6\\blender.exe",
            # "/home/dengel_to/Software/blender-3.6.5-linux-x64/blender",
            "-b", "cache/ParameterIter_v1-0Laptop_001/SpacecraftMotion.blend",
            "-P", "src/blender/Output/RenderFrame.py",
            "--", "--cycles-device", "OPTIX", 
            str(layer), str(frame), str(output_path)
        ]
        logging.info(f"Starting subprocess for render")
        frame_process = subprocess.Popen(
            render_command
            )
        return frame_process

    def get_gpu_memory_usage(self):
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,nounits,noheader'],
                                    stdout=subprocess.PIPE, universal_newlines=True)
            memory_used = [int(x) for x in result.stdout.strip().split('\n')]
            return memory_used
        except Exception as e:
            logging.error(f"Error: {e}")
            return None
    def get_gpu_memory_total(self):
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,nounits,noheader'],
                                    stdout=subprocess.PIPE, universal_newlines=True)
            memory_total = [int(x) for x in result.stdout.strip().split('\n')]
            return memory_total
        except Exception as e:
            logging.error(f"Error: {e}")
            return None

    def get_max_gpu_memory_usage(self, test_duration):

        # Get the current time
        start_time = time.time()
        max_gpu_memory_usage = 0
        # Run the loop for the specified duration
        while time.time() - start_time < test_duration:
            if max_gpu_memory_usage < self.get_gpu_memory_usage()[0]:
                max_gpu_memory_usage = self.get_gpu_memory_usage()[0]
            time.sleep(0.1)

        return max_gpu_memory_usage


