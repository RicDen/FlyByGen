import bpy
import numpy as np
import sys
import json
import os
import logging
# from src.utils.OutputLogger import OutputLogger

with open('src/config/paths.json', 'r') as f:
    paths = json.load(f)

sys.path.append(paths['project_directory'])



class RenderFrame:
    """
    This class creates the dataset of a defined scene from the currently opened blender file.
    The result will be rendered frames from all images with all the render layers defined in 
    the json file render.json.
    """
    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO)
        layer = sys.argv[8]
        frame = int(sys.argv[9])
        output_path = sys.argv[10]
        logging.info(f"Render subprocess starting with: \nLayer: {layer}\nFrame: {frame}\nOutput Path: {output_path} ")
        self.set_rendered_objects(layer)
        bpy.context.scene.render.filepath = f"{output_path}{frame:04d}.png"
        bpy.context.scene.frame_set(frame)
        bpy.ops.render.render(write_still=True)


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

RenderFrame()