import bpy
from math import radians as rad
import sys
import json
import logging
with open('src/config/paths.json', 'r') as f:
   paths = json.load(f)  

sys.path.append(paths['project_directory'])


class SceneGenerator:
    """
    Class generating the fundamental scene for the comet flyby
    It includes light settings, camera settings, world settings and saves the file as a basis for the next steps
    """
    # FEATURE: Allow setting of light parameters through function parameters
    def create_light(self):
        """
        Generates a scene light of the type SUN at location 200,0,0 with scale 1. The energy intensity is set to 33.

        :return: The generated light object which is the active object at this time in blender

        :rtype: bpy_struct, Object("Sun") as in bpy.data.objects['Sun']
        """
        logging.info("Setting lights...")
        # TODO: Refine brightness more
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.light_add(type='SUN',
                                 radius=1,
                                 align='WORLD',
                                 location=(200, 0, 0),
                                 scale=(1, 1, 1))
        bpy.context.object.data.energy = 33
        return bpy.context.active_object

    # FEATURE: Allow setting of camarea parameters through function parameters
    def create_camera(self):
        """
        Generates a camera with a predefined location and location
        
        :return: The generated camera object which is the active object at this time in blender

        :rtype: bpy_struct, Object("Camera") as in bpy.data.objects['Camera']
        """
        logging.info("Setting camera...")
        # Generating Camera
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.camera_add(enter_editmode=False,
                                  align='VIEW',
                                  location=(513.177, -360.99, 286.062),
                                  rotation=(rad(65.48), rad(0.77), rad(-305.47)),
                                  scale=(1, 1, 1))
        
        return bpy.context.active_object
            
    # BUG: Why starfield_Skydome_High_Resolution not working in documentation code
    # FEATURE: Allow exchange of world easier
    
    def create_world(self):
        """
        Sets the world environment to the given world data in the project
        
        A try and except is performed to test for the presence of the world background.
        """
        try:
            # World loading into scene(Stars)
            world = bpy.data.worlds['Starfield_Skydome_High_Resolution_16384x8192']
            bpy.context.scene.world = world
            logging.info("Set World...")
        except KeyError as e :
            logging.warning(f": Should only be missing during documentation{e}")



    def __init__(self):        
        self.light = self.create_light()

        self.main_camera = self.create_camera()
        self.create_world()
        
    # FEATURE implement functions to move the objects, the features shall not be static
    

