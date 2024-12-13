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
        scene_id = paths["pipeline_version"]+paths["number_of_generation"]
        combination_id = paths["combination"]
        start_frame = parameters["start_frame"]
        end_frame = parameters["end_frame"]
        render_layers = parameters["render_layers"]
        if end_frame < start_frame:
            logging.error(f"Start frame number must be smaller than end frame number!"+
                      "Check the render.json for the correct definition")
        processes = []
        gpu_iterator = 0
        gpu_list = ['2','3']
        threshold_factor = 10
        load_delay = 2
        render_number = (end_frame+1) * len(render_layers)
        logging.info(f"Rendering {render_number} frames...")
        self.gpu_min_required_memory = 0
        for frame in range(start_frame, end_frame + 1):
            logging.info(f"Rendering frame: {frame}...")
            for layer, object_name in render_layers.items():
                logging.info(f"Rendering layer: {layer}...")
                frame_output_path = os.path.join(
                    output_dir, f"{scene_id}",f"{combination_id}", f"{layer}", f"frame_")
                logging.info(f"Frame Output path: {frame_output_path}")
                
                while True:
                    gpu_index = gpu_list[gpu_iterator % len(gpu_list)]
                    logging.info(f"GPU iterator at {gpu_iterator} selecting GPU {gpu_index}")
                    gpu_iterator = gpu_iterator + 1
                    logging.info(f"Check if GPU {gpu_index} is ready...")
                    if  self.gpu_controller(gpu_index):
                        logging.info(f"GPU {gpu_index} is ready...")  
                        frame_process = self.render_frame(object_name, frame, frame_output_path, gpu_index)
                        break
                    else: 
                        logging.warning(f"Waiting for GPU {gpu_index} memory to become available...")
                
                if self.gpu_min_required_memory == 0:
                    logging.info(f"Setting GPU memory threshold...")
                    max_gpu_memory_usage = self.get_max_gpu_memory_usage(15, gpu_index)
                    logging.info(f"Maximum GPU usage is: {max_gpu_memory_usage}")
                    self.gpu_min_required_memory = max_gpu_memory_usage * threshold_factor
                    logging.info(f"GPU memory threshold set to: {self.gpu_min_required_memory}")                                    
                processes.append(frame_process)
                logging.info(f"There have been {len(processes)} out {render_number} started.")
            
        for process in processes:
            process.wait()
            
    def gpu_controller(self, gpu_index, load_delay=4):
        try:
            logging.info(f"Loading delay for {load_delay} seconds...")
            time.sleep(load_delay)
            # Fetch the memory usage and free memory for all GPUs
            memory_used = self.get_gpu_memory_usage()
            memory_free = self.get_gpu_memory_free()

            # Ensure the specified GPU index is valid
            if gpu_index not in memory_used or gpu_index not in memory_free:
                logging.error(f"Invalid GPU index: {gpu_index}")
                logging.error(f"Available GPUs: {memory_used.keys()}")
                return False

            # Get memory usage and free memory for the specified GPU
            used_memory = memory_used[gpu_index]
            free_memory = memory_free[gpu_index]

            # Log the memory info for the specific GPU
            logging.info(f"GPU {gpu_index} - Used memory: {used_memory} MiB")
            logging.info(f"GPU {gpu_index} - Free memory: {free_memory} MiB")

            # Calculate the memory threshold

            # If the free memory is less than the threshold, wait and retry
            if free_memory < (self.gpu_min_required_memory):
                logging.warning(f"Available GPU {gpu_index} memory utilisation ({free_memory}) is below minimum requirement ({self.gpu_min_required_memory}). Waiting for {load_delay} seconds.")
                return False

            # Proceed with the task if the memory is above the threshold
            logging.info(f"Enough GPU {gpu_index} memory ({free_memory}) is available (min: {self.gpu_min_required_memory}). Proceeding with task.")
            
            return True

        except Exception as e:
            logging.error(f"Error in GPU controller: {e}")
    
    def render_frame(self, layer, frame, output_path, gpu_index = 3):
        # Set the environment variable to control which GPU is used
        # The GPU index corresponds to the system GPU IDs (starting from 0)
        cuda_visible_devices = str(gpu_index)
        
        # Logging the GPU being used and the command
        logging.info(f"Starting subprocess for render on GPU {gpu_index}")
        
        # Set the environment variable for CUDA_VISIBLE_DEVICES
        env = os.environ.copy()
        env["CUDA_VISIBLE_DEVICES"] = cuda_visible_devices
        render_command = [
            paths['blender_path'],
            "-b", paths['render_file'],
            "-P", paths['render_executable'],
            "--", "--cycles-device", "OPTIX", str(layer), str(frame), str(output_path)
        ]
        logging.info(f"Starting subprocess for render")
        
        frame_process = subprocess.Popen(
            render_command,
            env=env  # Pass the modified environment with GPU restrictions
            )
        
        return frame_process

    def get_gpu_memory_usage(self):
        """Get the memory used by each GPU in MiB."""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=memory.used', '--format=csv,nounits,noheader'],
                stdout=subprocess.PIPE, universal_newlines=True
            )
            # Result is a list of memory used by each GPU
            memory_used = [int(x) for x in result.stdout.strip().split('\n')]
            gpu_memory_usage = {f"{i}": mem for i, mem in enumerate(memory_used)}
            return gpu_memory_usage
        except Exception as e:
            logging.error(f"Error: {e}")
            return None

    def get_gpu_memory_free(self):
        """Get the free memory of each GPU in MiB."""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=memory.free', '--format=csv,nounits,noheader'],
                stdout=subprocess.PIPE, universal_newlines=True
            )
            # Result is a list of memory free for each GPU
            memory_free = [int(x) for x in result.stdout.strip().split('\n')]
            gpu_memory_free = {f"{i}": mem for i, mem in enumerate(memory_free)}
            return gpu_memory_free
        except Exception as e:
            logging.error(f"Error: {e}")
        return None


    def get_max_gpu_memory_usage(self, test_duration, gpu_index):

        # Get the current time
        start_time = time.time()
        max_gpu_memory_usage = 0
        # Run the loop for the specified duration
        while time.time() - start_time < test_duration:
            if max_gpu_memory_usage < self.get_gpu_memory_usage()[gpu_index]:
                max_gpu_memory_usage = self.get_gpu_memory_usage()[gpu_index]
            time.sleep(0.1)

        return max_gpu_memory_usage


