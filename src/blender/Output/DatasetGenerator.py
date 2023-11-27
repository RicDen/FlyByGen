import bpy
import numpy as np
import sys
import json
import logging
import os
import subprocess
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

        # Loop through frames and set each one
            # Loop through wanted layers for dataset and render each one
            # Parallelize rendering using subprocesses
        for frame in range(start_frame, end_frame + 1):
            logging.info(f"Rendering frame: {frame}...")
            
            processes = []
            for layer, object_name in render_layers.items():
                logging.info(f"Rendering layer: {layer}...")
                self.set_rendered_objects(object_name)
                frame_output_path = os.path.join(
                    output_dir, f"{scene_id}", f"{layer}", f"frame_")
                logging.info(f"Frame Output path: {frame_output_path}")
                render_command = [
                    "../Software/blender-3.6.5-linux-x64/blender",
                    "-b", "cache/SetUp_v1-1_001/SpacecraftMotion.blend",
                    "-o", frame_output_path,
                    "-f", str(frame),
                    "--", "--cycles-device", "OPTIX"
                ]
                frame_process = subprocess.Popen(
                    render_command
                    )
                
                processes.append(frame_process)
            
            for process in processes:
                process.wait()
                # bpy.context.scene.frame_set(frame)
                # bpy.ops.render.render(write_still=True)

# FEATURE: Make the activate and deactivation of materials more flexible
    def set_rendered_objects(self, material):
        """
        Sets the active layers for the render by activating the holdout of different materials
        
        Parameters:
            material (str): Defines the material to be active. Every other material which can be deactivated will be deactivated

        NOTE: This is a hard coded function as the math node numbers to de/activate the material are material specific
        """
        if material == "Dust.001":
            logging.info(f"Set dust channels...")
            bpy.data.materials["Dust.001"].node_tree.nodes["Math.020"].inputs[0].default_value = 0
            bpy.data.materials["AsteroidSurface.001"].node_tree.nodes["Math.029"].inputs[0].default_value = 1
        elif material == "AsteroidSurface.001":
            logging.info(f"Set nucleus channels...")
            bpy.data.materials["Dust.001"].node_tree.nodes["Math.020"].inputs[0].default_value = 1
            bpy.data.materials["AsteroidSurface.001"].node_tree.nodes["Math.029"].inputs[0].default_value = 0
        elif material == "all":
            logging.info(f"Set all channels...")
            bpy.data.materials["Dust.001"].node_tree.nodes["Math.020"].inputs[0].default_value = 0
            bpy.data.materials["AsteroidSurface.001"].node_tree.nodes["Math.029"].inputs[0].default_value = 0
        else:
            logging.error(
                f"Material {material} is not existing, and thus cannot be rendered. Check that the material was specifed correctly")
