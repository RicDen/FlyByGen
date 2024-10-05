import bpy
import math
import json
import logging
import random


class CameraPositionSweeper:
    def __init__(self):
        with open('src/config/paths.json', 'r') as f:
            self.paths = json.load(f)
        logging.info("Starting Camera Position Sweep")
        self.load_config(self.paths["CameraPositionSweep_config"])
        logging.info("Config loaded")
        self.set_camera_optics_as_fov()
        
        self.rotate_around_target_with_noise()
        
    def load_config(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)

        self.camera = config["camera"]
        self.obj_camera = bpy.data.objects[self.camera]
        bpy.context.scene.camera = self.obj_camera

        if self.obj_camera is None:
            bpy.ops.object.camera_add()
            self.obj_camera = bpy.context.object
            bpy.context.scene.camera = self.obj_camera
            logging.warning("No camera object found. Created a new camera object.")

        self.target = config["target"]
        self.obj_target = bpy.data.objects[self.target]
        self.camera_distance = config["camera_closest"][0]  # Use the distance from the config
        self.azimuth_range = config["azimuth_range"]
        self.elevation_range = config["elevation_range"]
        self.azimuth_steps = config["azimuth_steps"]
        self.elevation_steps = config["elevation_steps"]
        self.speed = config["speed"]
        self.fps = config["fps"]
        self.fov = config["fov"]
        self.clip_start = config["clip_start"]
        self.clip_end = config["clip_end"]
        self.randomization = config["randomization"]

    def rotate_around_target_with_noise(self):
        """Rotate the camera around the target with fixed steps, and add noise to the azimuth and elevation."""
        azimuth_angles = range(self.azimuth_range[0], self.azimuth_range[1] + 1, self.azimuth_steps)
        elevation_angles = range(self.elevation_range[0], self.elevation_range[1] + 1, self.elevation_steps)
        frame_count = 0

        for azimuth in azimuth_angles:
            for elevation in elevation_angles:
                # Add noise (randomization) around the current azimuth and elevation steps
                noisy_azimuth = azimuth + random.uniform(-self.randomization, self.randomization)
                noisy_elevation = elevation + random.uniform(-self.randomization, self.randomization)
                                
                # Compute the new position using spherical coordinates (with noise)
                x = self.camera_distance * math.cos(math.radians(noisy_elevation)) * math.cos(math.radians(noisy_azimuth))
                y = self.camera_distance * math.cos(math.radians(noisy_elevation)) * math.sin(math.radians(noisy_azimuth))
                z = self.camera_distance * math.sin(math.radians(noisy_elevation))

                # Set the camera's position
                self.obj_camera.location = (x, y, z)
                self.obj_camera.keyframe_insert(data_path="location", frame=frame_count)

                # Ensure the camera is looking at the target
                rot_to_target = self.look_at()
                self.obj_camera.rotation_euler = rot_to_target
                self.obj_camera.keyframe_insert(data_path="rotation_euler", frame=frame_count)

                logging.info(f"Frame {frame_count}: Camera Location: {self.obj_camera.location}")
                logging.info(f"Frame {frame_count}: Camera Rotation: {self.obj_camera.rotation_euler}")

                frame_count += 1

        logging.info("Finished rotating around target with noise")

    def look_at(self):
        """Calculate the rotation for the camera to look at the target."""
        direction = self.obj_target.location - self.obj_camera.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        return rot_quat.to_euler()

    def set_camera_optics_as_fov(self):
        """Set the camera's field of view and clipping distances."""
        self.obj_camera.data.lens_unit = 'FOV'
        self.obj_camera.data.angle = math.radians(self.fov)
        self.obj_camera.data.clip_start = self.clip_start
        self.obj_camera.data.clip_end = self.clip_end
