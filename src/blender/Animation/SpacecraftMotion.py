import bpy
import numpy as np
import sys
import json
import logging
import math
with open('src/config/paths.json', 'r') as f:
    paths = json.load(f)

sys.path.append(paths['project_directory'])


class SpacecraftMotion:
    """
    Time scale in seconds
    Space scale in kilometers
    FPS of simulation
    """

    def __init__(self):
        # Load parameters from JSON file
        with open(paths['spacecraftAnimation_config']) as json_file:
            parameters = json.load(json_file)

        # Create spacecraft objects and set their parent-child relationship
        spacecraft_objects = self.create_spacecraft_hierarchy(
            parameters["spacecraft_hierarchy"])

        # Call the function and provide the desired name, location, and rotation for the camera
        OPIC = self.create_camera("OPIC", location=(
            5, -5, 5), rotation=(1.0, 0, 0.8))

        # Set the camera optics with the field of view parameters
        self.set_camera_optics_as_fov(
            OPIC, parameters["rotation_parameters"]["Camera_OPIC"])
        OPIC.parent = spacecraft_objects["OPICOrigin"]

        self.constraint_trackto(
            'TRACK_Y', 'UP_Z', spacecraft_objects["end_point"], spacecraft_objects["start_point"])
        self.constraint_trackto(
            'TRACK_NEGATIVE_Z', 'UP_Y', spacecraft_objects["B2Propagator"], spacecraft_objects["end_point"])

        # Extract rotation and flyby parameters

        fps = parameters["fps"]
        exposure = parameters["exposure"]

        pos_start, pos_end, f_start, f_end = self.setup_flyby(
            parameters["fly_by_parameters"], fps)
        self.setup_rotations(
            parameters["rotation_parameters"], spacecraft_objects, fps)

        self.apply_linear_movement(
            spacecraft_objects["B2Propagator"], pos_start, pos_end, f_start, f_end)

        # FEATURE modularise to render and scene classes
        bpy.context.scene.render.motion_blur_shutter = fps*exposure
        bpy.data.lights['Sun'].energy = exposure*33.33/40E-6
        bpy.context.view_layer.update()

    def setup_rotations(self, rotation_params, spacecraft_objects, fps):
        """
        Set up spacecraft rotations based on the provided rotation parameters.

        Parameters:
            rotation_params (dict): A dictionary containing rotation parameters.
            spacecraft_objects (dict): A dictionary containing spacecraft objects.
            fps (int): Frames per second for animation.

        This function sets up the rotations for the spacecraft objects based on the provided
        rotation parameters. It applies the axis-angle rotation to various objects to create
        the desired animation.

        Example of rotation_params dictionary:
            rotation_params = {
                "B2_main_rotation": {"period": 4},
                "B2_precession": {"period": 100, "angle_deg": -15},
                "B2_nutation": {"period": 20, "angle_deg": 5},

            }

        Example of spacecraft_objects dictionary:
        
        .. code-block:: text
        
            spacecraft_objects = {
                "OPIC_main_pointing": <bpy.types.Object>,
                "OPIC_B2_precessing_rotation": <bpy.types.Object>,
                "NutatingAxis": <bpy.types.Object>,
                "PrecessingMisalignment": <bpy.types.Object>,
                "NutationMisalignment": <bpy.types.Object>,
                "B2Propagator": <bpy.types.Object>,
                "OPICOrigin": <bpy.types.Object>,
                "start_point": <bpy.types.Object>,
                "end_point": <bpy.types.Object>,
                "closest_point": <bpy.types.Object>,
                "OPIC": <bpy.types.Object>,

            }

        Note:
            The rotation parameters and spacecraft objects must be defined and set up correctly before calling this function.
        """

        logging.info(
            f"Creating spacecraft rotations as in {paths['spacecraftAnimation_config']}...")

        B2_main_rotation_period = rotation_params["B2_main_rotation"]["period"]
        B2_precession_period = rotation_params["B2_precession"]["period"]
        B2_precession_angle_deg = (
            rotation_params["B2_precession"]["angle_deg"])/(rotation_params["B2_precession"]["division"])
        B2_nutation_period = rotation_params["B2_nutation"]["period"]
        B2_nutation_angle_deg = (
            rotation_params["B2_nutation"]["angle_deg"])/(rotation_params["B2_nutation"]["division"])

        # Setting Euler rotations for different objects objects
        bpy.data.objects["PrecessingMisalignment"].rotation_euler = (
            0, np.radians(B2_precession_angle_deg), 0)
        bpy.data.objects["NutationMisalignment"].rotation_euler = (
            0, np.radians(B2_nutation_angle_deg), 0)

        # Applying axis-angle rotation to various objects
        self.apply_axis_angle_rotation_to_object(
            spacecraft_objects["OPIC_main_pointing"], (0, 0, 1), (B2_precession_period * fps), 0)
        self.apply_axis_angle_rotation_to_object(
            spacecraft_objects["OPIC_B2_precessing_rotation"], (0, 0, 1), (B2_nutation_period * fps), 0)
        self.apply_axis_angle_rotation_to_object(
            spacecraft_objects["NutatingAxis"], (0, 0, 1), (B2_main_rotation_period * fps), 0.)

        # Setting euler rotation for OPIC object
        bpy.data.objects["OPIC"].rotation_euler = (
            0, -np.radians(rotation_params["Camera_OPIC"]["FOV"]/rotation_params["Camera_OPIC"]["Tilt_max"]-rotation_params["Camera_OPIC"]["Tilt"]), 0)

    def setup_flyby(self, fly_by_params, fps):
        """
        Set up spacecraft flyby based on the provided flyby parameters.

        Parameters:
            fly_by_params (dict): A dictionary containing flyby parameters.
            fps (int): Frames per second for animation.

        This function sets up the flyby for the spacecraft objects based on the provided
        parameters. It calculates start and end position and frame.

        Example of rotation_params dictionary:

        .. code-block:: text
        
            fly_by_params = {
                "speed": 80,
                "t_start": -1220,
                "t_end": -1200,
                "closest_fly_by": [0, 400, 0],
                "fly_by_azimuth_degrees": 0

            }
            
        Note:
            The fly by parameters must be defined and set up correctly before calling this function.
        """
        # Extract fly-by parameters from the given dictionary
        speed = fly_by_params["speed"]
        t_start = fly_by_params["t_start"]/speed-20
        t_end = fly_by_params["t_end"]/speed
        closest_fly_by = np.asarray(fly_by_params["closest_fly_by"])
        fly_by_azimuth_degrees = fly_by_params["fly_by_azimuth_degrees"]

        l_start = t_start*speed
        l_end = t_end*speed

        # Calculating x-plane
        x_plane = np.cross(np.asarray([0, 0, 1]), closest_fly_by)
        x_plane = x_plane/np.linalg.norm(x_plane)

        # Calculating y-plane
        y_plane = np.cross(closest_fly_by, x_plane)
        y_plane = y_plane/np.linalg.norm(y_plane)

        # Calculating start position
        pos_start = x_plane*np.cos(np.radians(fly_by_azimuth_degrees))*l_start + \
            y_plane*np.sin(np.radians(fly_by_azimuth_degrees)) * \
            l_start+closest_fly_by

        # Calculating end position
        pos_end = x_plane*np.cos(np.radians(fly_by_azimuth_degrees))*l_end + \
            y_plane*np.sin(np.radians(fly_by_azimuth_degrees)) * \
            l_end+closest_fly_by

        # Setting calculated positions to objects
        bpy.data.objects["start_point"].location = (pos_start)
        bpy.data.objects["end_point"].location = (pos_end)
        bpy.data.objects["closest_point"].location = (closest_fly_by)

        # Calculating frame range
        f_start = 0
        f_end = int(np.abs(l_start-l_end)*fps/speed)
        bpy.context.scene.frame_start = f_start
        bpy.context.scene.frame_end = f_end
        return pos_start, pos_end, f_start, f_end

    def create_spacecraft_hierarchy(self, spacecraft_hierarchy):
        """
        Reads the given dictionary and creates all the spacecraft points with :func:`create_points_spacecraft()`. It also links the created object with the defined parent object.

        :param spacecraft_hierarchy: Dictionary containing all spacecraft points and parents
        :type spacecraft_hierarchy: dict
        :return: The dictionary of created spacecraft objects
        :rtype: dict
        """
        spacecraft_objects = {}
        for name, parent_name in spacecraft_hierarchy.items():
            parent_object = spacecraft_objects.get(parent_name, None)
            spacecraft_objects[name] = self.create_points_spacecraft(
                name, parent_object)
        return spacecraft_objects

    def create_points_spacecraft(self, name, parent=None):
        """
        Create a spacecraft point with an optional parent.

        :param name: The name of the spacecraft object.
        :type name: str
        :param parent: The parent object to link to (default: None).
        :type parent: bpy.types.Object
        :return: The created spacecraft object.
        :rtype: bpy.types.Object
        """
        spacecraft = bpy.data.objects.new(name, None)
        bpy.context.collection.objects.link(spacecraft)
        if (parent):
            spacecraft.parent = parent
        return spacecraft

    def create_camera(self, name, location=(0, 0, 0), rotation=(0, 0, 0)):
        """
        Function which creates a camera with given name, location, and rotation. It also links the camera to the seen and sets it as active.
        NOTE: Camera setting have to be specified with the :func:`set_camera_optics_as_fov()` function

        :param name: Defines the name of the camera
        :type name: str
        :param location: Array with the initial cooridinates of the camera in euler angles
        :type location: float[]
        :param rotation: Array with initialy rotation of the camera
        :type rotation: float[]
        :return: returns the created camera object
        :rtype: bpy.data.objects
        """
        # Create a new camera object
        camera_data = bpy.data.cameras.new(name)
        camera_object = bpy.data.objects.new(name, camera_data)

        # Set the camera's location and rotation
        camera_object.location = location
        camera_object.rotation_euler = rotation

        # Link the camera to the current scene
        bpy.context.collection.objects.link(camera_object)

        # Make the camera active and set it as the active scene camera
        bpy.context.view_layer.objects.active = camera_object
        bpy.context.scene.camera = camera_object
        return camera_object

    def set_camera_optics_as_fov(self, camera_object, camera_specs):
        """
        Sets the camera optics with the units as field of view.

        :param angle: The angle of the the field of view (default = 0.31765)
        :type angle: float
        :param clip_start: Closest rendering with this camera (default = 0.1)
        :type clip_start: float
        :param clip_end: Farthest rendering with this camera (default = 100000)
        :type clip_end: float
        """
        camera_object.data.lens_unit = 'FOV'
        camera_object.data.angle = math.radians(camera_specs['FOV'])
        camera_object.data.clip_start = camera_specs['clip_start']
        camera_object.data.clip_end = camera_specs['clip_end']

    def constraint_trackto(self, track_axis, up_axis, object, target):
        """
        Add a "Track To" constraint to the specified object, making it track a target.

        :param track_axis: The axis along which the object should track the target (e.g., 'TRACK_X', 'TRACK_NEGATIVE_Y', etc.).
        :type track_axis: str
        :param up_axis: The axis that should be aligned with the target's up direction (e.g., 'UP_X', 'UP_Y', etc.).
        :type up_axis: str
        :param object: The object to which the constraint will be added.
        :type object: bpy.types.Object
        :param target: The target object that the 'object' should track.
        :type target: bpy.types.Object
        """
        # Add the "Track To" constraint to the end_point object
        track_to_constraint = object.constraints.new(type='TRACK_TO')
        # Set the target and up_axis options for the constraint
        track_to_constraint.target = target
        track_to_constraint.track_axis = track_axis
        track_to_constraint.up_axis = up_axis
        object.constraints["Track To"].target = target

    def apply_linear_movement(self, obj, start, end, frame_start, frame_end):
        """
        Apply linear movement animation to an object in Blender.

        :param obj: The object to animate.
        :type obj: bpy.types.Object
        :param start: The starting location of the object.
        :type start: tuple or list of three floats (x, y, z)
        :param end: The ending location of the object.
        :type end: tuple or list of three floats (x, y, z)
        :param frame_start: The starting frame for the animation.
        :type frame_start: int
        :param frame_end: The ending frame for the animation.
        :type frame_end: int
        """
        # Clear any existing animation data for the object
        obj.animation_data_clear()

        # Set the initial location of the object
        obj.location = start

        # Insert a keyframe at the starting frame with the initial location
        obj.keyframe_insert(data_path='location', frame=frame_start, index=-1)

        # Set the final location of the object
        obj.location = end

        # Insert a keyframe at the ending frame with the final location
        obj.keyframe_insert(data_path='location', frame=frame_end, index=-1)

        # Get the fcurves (animation curves) of the object's location
        fc = obj.animation_data.action.fcurves
        location_curve = fc[0]

        # Apply a cyclic modifier of type 'CYCLES' to the animation curve
        self.add_cycles_modifier(location_curve)

        # Set the extrapolation mode for the fcurve to 'LINEAR'
        location_curve.extrapolation = 'LINEAR'

        # Set the interpolation mode of each keyframe point to 'LINEAR'
        self.set_keyframe_interpolation(location_curve, 'LINEAR')

    def add_cycles_modifier(self, fcurve):
        """
        Add a 'CYCLES' modifier to the given fcurve.

        :param fcurve: The fcurve to add the modifier to.
        :type fcurve: bpy.types.FCurve
        """
        modifier = fcurve.modifiers.new(type='CYCLES')
        modifier.mode_before = 'NONE'
        modifier.mode_after = 'NONE'

    def set_keyframe_interpolation(self, fcurve, interpolation):
        """
        Set the interpolation mode for each keyframe point in the given fcurve.

        :param fcurve: The fcurve to set the keyframe interpolation for.
        :type fcurve: bpy.types.FCurve
        :param interpolation: The interpolation mode to set ('CONSTANT', 'LINEAR', 'BEZIER', etc.).
        :type interpolation: str
        """
        for kf in fcurve.keyframe_points:
            kf.interpolation = interpolation

    def apply_axis_angle_rotation_to_object(self, obj, axis, period_frames, phase=0.):
        """
        Apply axis-angle rotation to the object.

        :param obj: The object to apply rotation to.
        :type obj: bpy.types.Object
        :param axis: The axis of rotation as a tuple (x, y, z).
        :type axis: tuple
        :param period_frames: The number of frames for one complete rotation.
        :type period_frames: int
        :param phase: The initial phase angle in degrees (default: 0).
        :type phase: float
        """
        obj.animation_data_clear()
        obj.rotation_mode = 'AXIS_ANGLE'
        obj.rotation_axis_angle = (phase, axis[0], axis[1], axis[2])
        obj.keyframe_insert(data_path='rotation_axis_angle', frame=0, index=-1)
        obj.rotation_axis_angle = (
            phase+np.radians(360), axis[0], axis[1], axis[2])
        obj.keyframe_insert(data_path='rotation_axis_angle',
                            frame=period_frames, index=-1)
        fc = obj.animation_data.action.fcurves
        rotationZ = fc[0]
        modifier = rotationZ.modifiers.new(type='CYCLES')
        modifier.mode_before = 'REPEAT'
        modifier.mode_after = 'REPEAT'
        rotationZ.extrapolation = 'LINEAR'

        for kf in rotationZ.keyframe_points:
            kf.interpolation = 'LINEAR'
