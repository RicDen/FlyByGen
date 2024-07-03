from mathutils import Vector, noise, Matrix
from math import radians
import bmesh
import bpy
import sys
import json
import logging
with open('src/config/paths.json', 'r') as f:
    paths = json.load(f)

sys.path.append(paths['project_directory'])


# FEATURE: Check how the cores overlap and test if reasonable
# FEATURE: parameter range and automatic adaption of for example displacement of texture depending on comet size


class NucleusGenerator:
    """
    Class responsible for generating nucleus objects out of multiple cores, merging them and modifing them to make them look like a comet
    """

    def __init__(self):
        self.core_generators = {}
        """
        Initialize the NucleusGenerator.
        Json file needs to have the cores first in the file from top to bottom.
        Addons cannot be reused for multiple cores
        It creates cores from a json file and performs adaptations on it. 
        Noise verticles for object creation before remesh, not bigger than 0.7
        noise verticles after merge smaller 0.5
        noise displacing one: strenght below 0.7 and size smaller than 2
        Noise displacement two: strenght below 0.3 and size below 0.7
        """
        
        # Load data from JSON file
        with open(paths["nucleus_config"]) as json_file:
            core_config = json.load(json_file)
        cores = self.create_and_merge_cores_from_json(
            core_config)
        
        # FEATURE Enhance json file modularity
        for core_name, core_data in core_config["cores"].items():
            try: 
                cores[core_name]
                core = cores[core_name]

                self.remesh = Nucleus_modulator.mod_remesh_sharp(
                    core, core_data["remesh"])
                Nucleus_modulator.apply_modifier(self.remesh)
                Nucleus_modulator.noise_vertices(core, core_data["noise_vertices_2"])

                if "noise_displace_rough" in core_data:
                    noise_displace_rough_data = core_data["noise_displace_rough"]
                    self.noise_displace_rough = Nucleus_modulator.mod_noise_displace(core, noise_displace_rough_data["strength"], noise_displace_rough_data["size"])
                    Nucleus_modulator.apply_modifier(self.noise_displace_rough)

                if "noise_displace_fine" in core_data:
                    noise_displace_fine_data = core_data["noise_displace_fine"]
                    self.noise_displace_fine = Nucleus_modulator.mod_noise_displace(core, noise_displace_fine_data["strength"], noise_displace_fine_data["size"])
                    Nucleus_modulator.apply_modifier(self.noise_displace_fine)

                self.subdivision = Nucleus_modulator.mod_add_subdivision(core, core_data["subdiv2"], core_data["subdiv2"])
                Nucleus_modulator.apply_modifier(self.subdivision)
                Nucleus_modulator.set_smooth(True)

                TextureHandler.material_link("AsteroidSurface.001", core)
                TextureHandler.material_displacement("AsteroidSurface.001", 2.4)
            except:
                logging.info(f"Created all cores")
                pass


    def create_and_merge_cores_from_json(self, core_config):
        """
        Create and merge cores based on data from the dictionary taken from the json file.

        This function reads data from a dictionary containing information about the cores and merge operations.
        It creates core objects with specified parameters, performs transformations on the cores,
        merges the cores together, and returns a dictionary of the created core objects.

        :param json_file: Path to the JSON file containing core and merge data.
        :type json_file: str
        :return: Dictionary containing the core objects with their names as keys.
        :rtype: dict
        """

        core_objects = {}

        # Create cores and perform operations
        for core_name, core_data in core_config["cores"].items():
            subdiv = core_data['subdiv']
            radius = core_data['radius']
            translation = core_data['translation']
            rotation = core_data['rotation']
            shape = core_data['shape']
            noise_vertices = core_data['noise_vertices']

            # Create core
            self.create_core(core_name, subdiv, radius)
            core = self.get_core(core_name)

            # Perform transformations
            core.translate(translation)
            core.rotate(rotation)
            core.shape(shape)
            Nucleus_modulator.noise_vertices(core, noise_vertices)

            core_objects[core_name] = core
        # Merge cores
        for merge_data in core_config['merge']:

            # FEATURE: Test how overlap and react accordingly
            # FEATURE: Integrate multi core option
            core_name = merge_data['core']
            addon_name = merge_data['addon']

            if core_name in core_objects and addon_name in core_objects:
                core = core_objects[core_name]
                addon = core_objects[addon_name]
                self.core_merger(core, addon)
                self.object_cleaner(addon)
            else:
                logging.error(f"The merging of {core_name} and {addon_name} failed. Either"
                              +"one or neither of them have not been crated. Check the nucleus.json"
                              +"to make sure all merge objects are existing")

        # Clean up project
        self.project_cleaner()

        # Filter out addons
        core_objects = {name: core for name,
                        core in core_objects.items() if "addon" not in name}

        return core_objects

    def create_core(self, core_name, subdiv, radius):
        """
        Create a new core using CoreGenerator and store it in the core_generators dictionary.

        :param core_name: The name the core shall have.
        :type core_name: str
        :param subdiv: The number of subdivisions for the core.
        :type subdiv: int
        :param radius: The radius of the core.
        :type radius: float
        """
        logging.info(f"Creating a new core: {core_name}")
        core_generator = CoreGenerator()
        core_generator.create(core_name, subdiv, radius)
        self.core_generators[core_name] = core_generator

    def get_core(self, core_name):
        """
        Get a specific core from the core_generators dictionary.

        :param core_name: The name of the core to retrieve.
        :type core_name: str
        :return: The CoreGenerator object representing the core, or None if not found.
        :rtype: bpy.types.object
        """
        if core_name in self.core_generators:
            return self.core_generators[core_name]
        else:
            return None

    def core_merger(self, core, addon):
        """
        Merges the core with an according addon
        :param core: the object the addon shall be added to
        :type core: bpy.types.object
        :param addon: the object which is added to the core
        :type addon: bpy.types.object
        """
        logging.info(f"Merging {core.object.name} with {addon.object.name}...")
        core.object.select_set(True)
        bpy.context.view_layer.objects.active = core.object

        bpy.ops.object.modifier_add(type='BOOLEAN')
        # Get a reference to the newly added modifier
        boolean_modifier = bpy.context.object.modifiers[-1]

        # Set the properties of the boolean modifier
        boolean_modifier.operation = 'UNION'
        boolean_modifier.solver = 'FAST'
        # boolean_modifier.object = bpy.data.objects[addon.object]
        boolean_modifier.object = addon.object
        # Apply the modifier
        bpy.ops.object.modifier_apply(modifier="Boolean", report=True)

    def object_cleaner(self, removable_object):
        """
        Cleans the project of a specified object. Usually applied after merging was performed
        :param removable_object: The object to be removed
        :type removable_object: bpy.types.Object
        """
        logging.info(f"Cleaning objects...")
        # Check if the object exists
        if removable_object is not None:
            # Remove the object from the scene
            bpy.data.objects.remove(removable_object.object, do_unlink=True)

        # Iterate over all meshes in the data blocks
        for mesh in bpy.data.meshes:
            # Check if the mesh is unused
            if mesh.users == 0:
                # Remove the mesh from the data blocks
                bpy.data.meshes.remove(mesh)

    # def position()
        # Set new core to position which is randomly given

    # def orientation()

    # def is_overlap()

    def project_cleaner(self):
        """
        Cleans the project of unused textures to avoid that the project file gets too big
        """
        logging.info(f"Cleaning project...")
        # Iterate over all textures in the data blocks
        for texture in bpy.data.textures:
            # Check if the texture is unused
            if texture.users == 0:
                # Remove the texture from the data blocks
                bpy.data.textures.remove(texture)


# used to create sub cores as many as needed
# add modularily names to the objects etc.
# Create the core_ object. This should be the dominating body
class CoreGenerator:
    """
    Class responsible for generating core objects.
    """

    def __init__(self):
        """
        Initialize the CoreGenerator.
        """
        self.object = None

    def create(self, obj_name, subdiv, radius):
        """
        Create a new icosphere object in Blender and assign it to the CoreGenerator.
        Multiple of these objects can with the core_merger function be merged into one nucleus.

        :param obj_name: The name of the icosphere object.
        :type obj_name: str
        :param subdiv: The number of subdivisions for the icosphere.
        :type subdiv: int
        :param radius: The radius of the icosphere.
        :type radius: float
        """
        logging.info(f"Creating sphere: {obj_name}...")
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=subdiv, radius=radius)
        self.object = bpy.context.active_object
        self.object.name = obj_name

    def translate(self, location):
        """
        Translate the icosphere object.

        :param location: The translation vector (x, y, z).
        :type location: list [float]
        """

        logging.info(f"Translating object: {self.object.name}...")
        self.object.location = location

    def scale(self, scale):
        """
        Scale the icosphere object.

        :param scale: The scale factors for each axis (x, y, z).
        :type scale: list [float]
        """
        logging.info(f"Scaling object: {self.object.name}...")
        self.object.scale = scale

    def shape(self, transform):
        """
        Function to transform the object into any ellipsoid out of a sphere.

        :param transform: The scale of each axis into which the object should be stretched. "transform" is a list of three values for x,y,z axis.
        :type transform: list[float]
        """

        logging.info(f"Shaping object: {self.object.name}...")
        new_core_transform = Matrix.Scale(transform[0], 4, (1, 0, 0)) @ Matrix.Scale(
            transform[1], 4, (0, 1, 0)) @ Matrix.Scale(transform[2], 4, (0, 0, 1))
        self.object.data.transform(new_core_transform)

    def rotate(self, rotation):
        """
        Rotate the icosphere object.

        :param rotation: The rotation angles (in degrees) around the X, Y, and Z axes.
        :type rotation: list[float]
        """
        logging.info(f"Rotating object: {self.object.name}...")
        self.object.rotation_euler[0] += radians(rotation[0])
        self.object.rotation_euler[1] += radians(rotation[1])
        self.object.rotation_euler[2] += radians(rotation[2])


class TextureHandler:
    """
    Controls and configures the textures in the project
    """
    # DOC: add documentation for texture_handler
    # TEATURE: Add more texture functionatlities, like adaptations and other textures
    def material_link(material, target_object):
        """
        Links the given texture to the target object.
        :param target_object: The object the texture should be applied to
        :type target_object: bpy.types.Object
        """
        try:
            logging.info(
                f"Linking material to object: {target_object.object.name}...")
            mat_asteroid = bpy.data.materials[material]
            target_object.object.data.materials.append(mat_asteroid)
        except KeyError as e:
            logging.warning(
                f": Asteroid material should only be missing during documentation{e}")

    def material_displacement(material, intensity):
        """
        Adapts the displacement properties of the material. The bigger the comet is the higher the value has to be.
        If the comet looks too smooth and is missing an asteroid "roughness", then the intensity is likely too low.
        If the comet looks very rough and exagerated shape, then the intensity is likely too high.

        :param material: The name of the material which should be used
        :type material: str
        :param target_object: The object the texture should be applied to
        :type target_object: bpy.types.Object
        """
        try:
            logging.info(f"Adapting material displacement...")
            bpy.data.materials[material].node_tree.nodes["Displacement"].inputs[2].default_value = intensity
        except KeyError as e:
            logging.warning(
                f": Asteroid material should only be missing during documentation{e}")

class Nucleus_modulator:
    """
    Class which provides all functionalities needed to adapt the comet as needed.
    NOTE:Some of these functions can perform fairly detailed shape adaptations, however, they might be overwritten by a texture displacement
    """

    def mod_remesh_voxel(target_object, voxel_size, shade):
        """
        Remeshes the mesh. Mostly used after merging to objects

        :param target_object: the object given to the function where the remesh shall be applied to
        :type target_object: bpy.types.Object
        :param voxel_size: The voxel size for the remesh
        :type voxel_size: float
        :param shade: Defines the shading mode True = Smooth, False = Flat
        :type shade: Boolean
        """
        logging.info(f"Performing remesh of all...")
        mod_remesh = target_object.object.modifiers.new(
            name='RemeshVoxel', type='REMESH')
        mod_remesh.mode = 'VOXEL'
        mod_remesh.voxel_size = voxel_size
        mod_remesh.use_smooth_shade = shade
        return mod_remesh.name

    def mod_remesh_sharp(target_object, remesh_param):
        """
        Remeshes the mesh with the sharp sessing. Mostly used after merging to objects to get the mesh equally distributed

        :param target_object: the object given to the function where the remesh shall be applied to
        :type target_object: bpy.types.Object
        :param octree_depth: The depth of the octree used for remeshing. Higher values result in finer details.
        :type octree_depth: int
        :param scale: The scaling factor for the remeshing operation. Values between 0.1 and 1.0 are recommended.
        :type scale: float
        :param sharpness: Higher values produce sharper edges.
        :type sharpness: float
        """
        logging.info(f"Performing remesh of all...")
        mod_remesh = target_object.object.modifiers.new(
            name='RemeshSharp', type='REMESH')
        mod_remesh.mode = 'SHARP'
        mod_remesh.octree_depth = remesh_param['octree']
        mod_remesh.scale = remesh_param['scale']
        mod_remesh.sharpness = remesh_param['sharpness']
        mod_remesh.use_smooth_shade = remesh_param['shade']
        return mod_remesh.name

    def noise_vertices(target_object, noise_intensity):
        """
        This adapts the verticles of the object randomly. The result is random but depends on the amount of subdivisions and the noise intensity

        :param target_object: the object given to the function where the noise shall be applied to
        :type target_object: bpy.types.Object
        :param noise_intensity: The intensity of the noise to be applied
        :type noise_intensity: int
        """
        logging.info(f"Applying noise to {target_object.object.name}...")
        for v in target_object.object.data.vertices:
            coreMerge_noise_vector = Vector(
                (noise.random(), noise.random(), noise.random())) * noise_intensity
            v.co += coreMerge_noise_vector


    def mod_add_subdivision(target_object, levels, render_levels):
        """
        Add a subdivision modifier to the target object.

        :param target_object: The object to add the subdivision modifier to.
        :type target_object: bpy.types.Object
        :param levels: The number of subdivision levels in the viewport.
        :type levels: int
        :param render_levels: The number of subdivision levels in the final render.
        :type render_levels: int
        """
        logging.info(f"Adding subdivisions to {target_object.object.name}...")
        mod_subdiv = target_object.object.modifiers.new(
            name='Subdiv', type='SUBSURF')
        mod_subdiv.levels = levels
        mod_subdiv.render_levels = render_levels
        return mod_subdiv.name

    def mod_noise_displace(target_object, strength, noise_scale):
        """
        Add a noise displace modifier to the target object.

        :param target_object: The object to add the noise displace modifier to.
        :type target_object: bpy.types.Object
        :param strength: The strength of the displace effect.
        :type strength: float
        :param noise_scale: The scale of the noise texture.
        :type noise_scale: float
        """
        logging.info(
            f"Adding noise displacement to {target_object.object.name}...")
        mod_displace = target_object.object.modifiers.new(
            name='Displace', type='DISPLACE')
        mod_displace.strength = strength
        mod_displace.texture = bpy.data.textures.new(
            name='Noise_Displace', type='STUCCI')
        mod_displace.texture.noise_scale = noise_scale
        return mod_displace.name

    def set_smooth(smooth):
        """
        Sets the object visuals to smooth

        :param smooth: True for smooth, False for flat shade (not smooth)
        :type smooth: boolean
        """
        if (smooth == True):
            logging.info(f"Setting to smooth shade...")
            bpy.ops.object.shade_smooth()
        else:
            logging.info(f"Setting to flat shade...")
            bpy.ops.object.shade_flat()

    def apply_modifier(modifier_name):
        """
        Applies created modifier. It has to performed at certain steps to avoid interference between the different modifiers

        :param modifier_name: Apply the given modifier according to the specified name
        :type modifier_name: str
        """
        logging.info(f"Applying modifier{modifier_name}...")
        bpy.ops.object.modifier_apply(modifier=modifier_name, report=True)
