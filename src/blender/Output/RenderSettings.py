#Render settings
#This file sets all render settings and the output properties

import bpy
import sys
import json
with open('src/config/paths.json', 'r') as f:
   paths = json.load(f)  

sys.path.append(paths['project_directory'])
# TODO: Add feature to define every setting by function call through json defined values
# FEATURE: Add render exposure settings as in found in film

class RenderSettings:
    """
    This class defines all areas of the render settings in blender
    """

    @staticmethod
    def set_cycles(cycles_config):
        """
        Sets all cycles related settings such as experimental settings and GPU enabled or not
        :param cycles_config (dict): A dictionary containing the needed cycles settings
        
        Example of cycles_config dictionary:
        
        .. code-block:: text

            "cycles":{
                "experimental": true,
                "GPU": true
                }

        """
        #Set render engine to cycle
        bpy.context.scene.render.engine = 'CYCLES'
        # Allow experimental feature set
        if(cycles_config["experimental"] == True):
            bpy.context.scene.cycles.feature_set = 'EXPERIMENTAL'
        else:
            bpy.context.scene.cycles.feature_set = 'SUPPORTED'

        # Use GPU?
        if (cycles_config["GPU"] == True):
            print("Set GPU...")
            bpy.context.scene.cycles.device = 'GPU'


    @staticmethod
    def set_viewport_samples(viewport_config):
        """
        Sets the viewport settings. Settings should be set to low values to allow a smooth preview in blender itself
        :param viewport_config (dict): A dictionary containing the needed viewport settings
        
        Example of viewport_config dictionary:
        
        .. code-block:: text

            "viewport":{
                "preview_adaptive_sampling": false,
                "preview_samples": "16"
            }

        """
        bpy.context.scene.cycles.use_preview_adaptive_sampling = viewport_config["preview_adaptive_sampling"]
        bpy.context.scene.cycles.preview_samples = viewport_config["preview_samples"]

    @staticmethod
    def set_render_samples(render_samples_config):
        """
        Sets the render sample settings according to dictionary given
        :param render_samples_config (dict): A dictionary containing the needed render samples settings
        
        Example of render_samples_config dictionary:
        
        .. code-block:: text

            "render_samples":{
                "use_adaptive_sampling": false,
                "samples": 512,
                "use_denoising": true,
                "denoiser": "OPTIX"
            }

        """
        bpy.context.scene.cycles.use_adaptive_sampling = render_samples_config["use_adaptive_sampling"]
        bpy.context.scene.cycles.samples = render_samples_config["samples"]
        bpy.context.scene.cycles.use_denoising = render_samples_config["use_denoising"]
        bpy.context.scene.cycles.denoiser = render_samples_config["denoiser"]

    @staticmethod
    def set_lightpaths(lightpaths_config):
        """
        Sets the lightpath complexity. This is especially relevant for rendering of dust and shadows
        Lightpaths settings are set according to dictionary given
        :param lightpaths_config (dict): A dictionary containing the needed lightpaths settings
        
        Example of lightpaths_config dictionary:
        
        .. code-block:: text

            "lightpaths":{
                "max_bounces": 128,
                "diffuse_bounces": 128,
                "glossy_bounces": 128,
                "transmission_bounces": 128,
                "volume_bounces": 128,
                "transparent_max_bounces": 128
            }

        """
        bpy.context.scene.cycles.max_bounces = lightpaths_config["max_bounces"]
        bpy.context.scene.cycles.diffuse_bounces = lightpaths_config["diffuse_bounces"]
        bpy.context.scene.cycles.glossy_bounces = lightpaths_config["glossy_bounces"]
        bpy.context.scene.cycles.transmission_bounces = lightpaths_config["transmission_bounces"]
        bpy.context.scene.cycles.volume_bounces = lightpaths_config["volume_bounces"]
        bpy.context.scene.cycles.transparent_max_bounces = lightpaths_config["transparent_max_bounces"]

    @staticmethod
    def set_motion_blur(motion_blur_config):
        """
        Sets motion blur settings
        Motion blur settings are set according to dictionary given
        :param motion_blur_config (dict): A dictionary containing the needed motion blur settings
        
        Example of motion_blur_config dictionary:
        
        .. code-block:: text

            "motion_blur":{
                "use_motion_blur": true,
                "motion_blur_position": "CENTER",
                "motion_blur_shutter": 0.001,
                "rolling_shutter_type": "NONE"
            }

        """
        bpy.context.scene.render.use_motion_blur = motion_blur_config["use_motion_blur"]
        bpy.context.scene.cycles.motion_blur_position = motion_blur_config["motion_blur_position"]
        bpy.context.scene.render.motion_blur_shutter = motion_blur_config["motion_blur_shutter"]
        bpy.context.scene.cycles.rolling_shutter_type = motion_blur_config["rolling_shutter_type"]

    @staticmethod
    def set_color_management(color_management_config):
        """
        Sets the render color management
        The color management settings are set according to dictionary given
        :param color_management_config (dict): A dictionary containing the needed color management settings
        
        Example of color_management_config dictionary:
        
        .. code-block:: text

            "color_management":{
                "display_device": "sRGB",
                "view_transform": "Raw",
                "look": "None",
                "exposure": 0,
                "gamma": 1,
                "sequencer_colorspace_settings": "sRGB"
            }

        """
        bpy.context.scene.display_settings.display_device = color_management_config["display_device"]
        bpy.context.scene.view_settings.view_transform = color_management_config["view_transform"]
        bpy.context.scene.view_settings.look = color_management_config["look"]
        bpy.context.scene.view_settings.exposure = color_management_config["exposure"]
        bpy.context.scene.view_settings.gamma = color_management_config["gamma"]
        bpy.context.scene.sequencer_colorspace_settings.name = color_management_config["sequencer_colorspace_settings"]


    @staticmethod
    def set_output_format(output_format_config):
        """
        Defines the output format and properties
        Output format and properties settings are set according to dictionary given
        :param output_format_config (dict): A dictionary containing the needed Output format and properties settings
        
        Example of output_format_config dictionary:
        
        .. code-block:: text

            "output_format":{
                "resolution_x": 2048,
                "resolution_y": 2048,
                "pixel_aspect_x": 1,
                "pixel_aspect_y": 1
            }

        """
        bpy.context.scene.render.resolution_x = output_format_config["resolution_x"]
        bpy.context.scene.render.resolution_y = output_format_config["resolution_y"]

        bpy.context.scene.render.pixel_aspect_x = output_format_config["pixel_aspect_x"]
        bpy.context.scene.render.pixel_aspect_y = output_format_config["pixel_aspect_y"]

    # FEATURE: Consider creating own animation render json + class.
    @staticmethod
    def set_framerange(framerange_config):
        """
        Defines the start, end and step for sequence renders which could be used for animation movies
        Framerange settings are set according to dictionary given
        :param framerange_config (dict): A dictionary containing the needed frame range settings
        
        Example of framerange_config dictionary:
        
        .. code-block:: text
        
            "framerange":{
                "frame_start": 0,
                "frame_end": 480,
                "frame_step": 1,
                "use_multiview": false
            }

        """
        bpy.context.scene.frame_start = framerange_config["frame_start"]
        bpy.context.scene.frame_end = framerange_config["frame_end"]
        bpy.context.scene.frame_step = framerange_config["frame_step"]

        bpy.context.scene.render.use_multiview = framerange_config["use_multiview"]



    def __init__(self):
        with open(paths["render_configs"], 'r') as file:
            render_configs = json.load(file)
        self.set_cycles(render_configs["cycles"])
        self.set_viewport_samples(render_configs["viewport"])
        self.set_render_samples(render_configs["render_samples"])
        self.set_lightpaths(render_configs["lightpaths"])
        self.set_motion_blur(render_configs["motion_blur"])
        self.set_color_management(render_configs["color_management"])
        self.set_output_format(render_configs["output_format"])
        self.set_framerange(render_configs["framerange"])
