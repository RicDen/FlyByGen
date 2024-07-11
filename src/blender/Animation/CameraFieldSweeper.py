import bpy
import math
import json
import os
import logging

# config = {
#   "camera": "Camera",
#   "target": "core",
#   "camera_closest": [1000, 400, 0],
#   "camera_furthest": [2800, 400, 0],
#   "azimuth_range": [-9, 9],
#   "azimuth_steps": 2,
#   "elevation_range": [-9, 9],
#   "elevation_steps": 2,
#   "fov_range": [0,10],
#   "fov_steps": 5,
#   "clip_start": 0.1,
#   "clip_end": 100000,
#   "speed": 80,
#   "fps": 24,
#   "exposure": 40E-6
# }
  
  
class CameraFieldSweeper:
    def __init__(self):
        with open('src/config/paths.json', 'r') as f:
           self.paths = json.load(f)
        logging.info("Starting Camera Sweep")
        self.load_config(self.paths["CameraFieldSweep_config"])
        logging.info("Config loaded")
        self.set_camera_optics_as_fov()
        
        self.sweep()
        
    def load_config(self, config_path):
        with open(config_path, 'r') as f:
           config = json.load(f)

        self.camera = config["camera"]
        self.obj_camera = bpy.data.objects[self.camera]
        self.target = config["target"]
        self.obj_target = bpy.data.objects[self.target]
        self.camera_closest = config["camera_closest"]
        self.camera_furthest = config["camera_furthest"]
        self.azimuth_range = config["azimuth_range"]
        self.elevation_range = config["elevation_range"]
        self.azimuth_steps = config["azimuth_steps"]
        self.elevation_steps = config["elevation_steps"]
        self.fov_range = config["fov_range"]
        self.fov_steps = config["fov_steps"]
        self.speed = config["speed"]
        self.fps = config["fps"]
        self.fov = config["fov"]
        self.clip_start = config["clip_start"]
        self.clip_end = config["clip_end"]
        

    def sweep(self):
        #FEATURE: allow moving in multiple directions
        self.camera_distances = range(self.camera_closest[0], self.camera_furthest[0], self.speed)
        self.azimuth_angles = range(self.azimuth_range[0], self.azimuth_range[1], self.azimuth_steps)
        self.elevation_angles = range(self.elevation_range[0], self.elevation_range[1], self.elevation_steps)
        logging.info(f"Azimuth angles: {self.azimuth_angles}")
        frame_count = 0
        for distance in self.camera_distances:
            for azimuth in self.azimuth_angles:
                for elevation in self.elevation_angles:
                    
                    bpy.context.scene.frame_set(frame_count)
                    self.obj_camera.location = (distance, self.camera_closest[1], self.camera_closest[2])
                    self.obj_camera.keyframe_insert(data_path="location", frame=frame_count)
                    rot_to_target = self.look_at()
                    self.obj_camera.rotation_euler = rot_to_target
                    self.obj_camera.keyframe_insert(data_path="rotation_euler", frame=frame_count)
                    logging.info(f"Camera Location: {self.obj_camera.location}")
                    logging.info(f"Camera Rotation: {self.obj_camera.rotation_euler}")
                    # Adjust rotation incrementally
                    self.obj_camera.rotation_euler[2] += math.radians(azimuth)
                    self.obj_camera.rotation_euler[0] += math.radians(elevation)
                    
                    
                    # Insert keyframes for the new orientation
                    self.obj_camera.keyframe_insert(data_path="rotation_euler", frame=frame_count)
                    
                    logging.info(f"Frame {frame_count}: Camera Location: {self.obj_camera.location}")
                    logging.info(f"Frame {frame_count}: Camera Rotation: {self.obj_camera.rotation_euler}")
                    frame_count += 1

        logging.info("Finished sweep")
    

    
    def look_at(self):
        
        # Calculate the direction from the camera to the target
        direction = self.obj_target.location - self.obj_camera.location
        
        # Get the rotation quaternion that points the camera in the direction of the target
        rot_quat = direction.to_track_quat('-Z', 'Y')
        
        # Set the camera rotation
        return rot_quat.to_euler()
    
    def set_camera_optics_as_fov(self):
        """
        Sets the camera optics with the units as field of view.

        :param angle: The angle of the the field of view (default = 0.31765)
        :type angle: float
        :param clip_start: Closest rendering with this camera (default = 0.1)
        :type clip_start: float
        :param clip_end: Farthest rendering with this camera (default = 100000)
        :type clip_end: float
        """
        self.obj_camera.data.lens_unit = 'FOV'
        self.obj_camera.data.angle = math.radians(self.fov)
        self.obj_camera.data.clip_start = self.clip_start
        self.obj_camera.data.clip_end = self.clip_end

# CameraFieldSweeper()