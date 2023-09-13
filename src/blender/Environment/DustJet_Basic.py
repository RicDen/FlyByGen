import bpy
import sys
import json
import logging
with open('src/config/paths.json', 'r') as f:
   paths = json.load(f)

sys.path.append(paths['project_directory'])


class DustJetGenerator:

    def __init__(self, core_object = "core"):  
        # FEATURE: Figure out way to know objects created in the nucleus creator to apply dust jets to the correct object (pass "core_object)")
        # FEATURE: Dust cloud is limited by cylinders, should be removed
        # FEATURE: Add default dictionary instead of all parameters in function head and pass just dictionaries on.
        # This will allow more modular code and no need to change function parameters
        
        emitter = self.create_environment_objects(core_object)
        self.apply_dust_material(emitter, "Emitter.001")
        # define the particle system with particle_kind = "somename"
        particle_settings = self.mod_create_and_config_particles("jets")
        self.particles_set_texture(emitter, particle_settings)
        self.emitter_render_settings(emitter)

    def create_environment_objects(self, core_object):
        """
        Duplicates the targeted core object as basis for the particle system.
        The object will not be visible in the render, but its particle system will be

        :param core_object: Core object to attach dust jets too
        :type core_object: bpy.types.Object
        """
        logging.info(f"Creating dust base objects...")
        # Create all the objects needed to create the particle system
        # Select core
        core = bpy.context.collection.objects[core_object]
        # Create emitter mesh from core
        emitterMesh = core.data.copy()
        emitterMesh.name = "emitterMesh "+core_object
        # Create Object containing the emitter
        emitter = bpy.data.objects.new("emitter " + core_object, emitterMesh)
        # emitter.name = "Emitter"
        bpy.context.scene.collection.objects.link(emitter)
        emitter.parent = core
        return emitter

    def apply_dust_material(self, emitter_object, material):
        """
        :param emitter_object: The emitter object to be worked with
        :type emitter_object: bpy.types.Object
        :param material: Name of the material to be applied to the dust
        :type material: str
        """
        logging.info(f"Applying dust material...")
        try:
            mat_dust = bpy.data.materials[material]
            emitter_object.data.materials.append(mat_dust)
            bpy.context.view_layer.objects.active = emitter_object
            bpy.ops.object.material_slot_remove()
        except KeyError as e:
            logging.warning(
                f": Should only be missing during documentation{e}")

    def load_particles_settings_from_json(self, json_file):
        with open(json_file, 'r') as file:
            particle_settings = json.load(file)
        return particle_settings

    def mod_create_and_config_particles(self, particle_kind="jets"):
        """
        Create and configure particle system settings for a given particle kind.

        This function creates and configures particle system settings based on the provided particle kind.
        It sets various parameters related to emission, velocity, rotation, physics, rendering, viewport display,
        children settings, field weights, and force fields.

        :param particle_kind: The kind of particles to configure (default: "jets").
        :type particle_kind: str
        :return: The particle settings object.
        :rtype: bpy.types.particle_settings
        """
        # FEATURE: Figure out where particles are turned to cylinder and make them animated
        # TODO: Create particle settings from json file with no need to define all parameters.
        # Load particle settings from JSON
        particle_config = self.load_particles_settings_from_json(
            paths['dustjet_config'])

        # Create and configure particles using the settings
        logging.info(f"Creating and naming particle system")
        bpy.ops.object.particle_system_add()
        bpy.data.particles[
            "ParticleSettings"].name = f"ParticleSettings_{particle_config['particle_kind']}"
        particle_settings = bpy.data.particles[
            f"ParticleSettings_{particle_config['particle_kind']}"]
        self.mod_particles_set_emission(
            particle_settings, **particle_config.get('emission_settings', {}))
        self.mod_particles_set_velocity(
            particle_settings, **particle_config.get('velocity_settings', {}))
        self.mod_particles_set_rotation(
            particle_settings, **particle_config.get('rotation_settings', {}))
        self.mod_particles_set_physics(
            particle_settings, **particle_config.get('physics_settings', {}))
        self.mod_particles_set_render(
            particle_settings, **particle_config.get('render_settings', {}))
        self.mod_particles_set_viewport(
            particle_settings, **particle_config.get('viewport_settings', {}))
        self.mod_particles_set_childern_interpolated(particle_settings, particle_config.get('children_parting'),
                                                     particle_config.get(
                                                         'children_clumping'),
                                                     particle_config.get(
                                                         'children_roughness'),
                                                     **particle_config.get('children_settings', {}))
        self.mod_particles_set_field(
            particle_settings, **particle_config.get('field_settings', {}))
        self.mod_particles_set_force(
            particle_settings, **particle_config.get('force_settings', {}))
        return particle_settings

    def mod_particles_set_emission(self, particle_settings, type='EMITTER', count=15000,
                                   seed=0, frame_start=1, frame_end=1, lifetime=500000,
                                   random=0, emit_from='FACE', use_modifier=True, distribution='RAND',
                                   emit_random=True, even_distribution=True):
        """
        Configure particle emission settings.

        :param particle_settings: The particle settings configuration to adapt.
        :type particle_settings: bpy.types.ParticleSettings
        :param type: The type of particle emission (default: 'EMITTER').
        :type type: str
        :param count: Number of emitter jets attached to the object. This decides how much dust will be generated (default: 15000).
        :type count: int
        :param seed: The seed value for randomizing particles (default: 0).
        :type seed: int
        :param frame_start: The frame where the particle emission starts (default: 1).
        :type frame_start: int
        :param frame_end: The frame where the particle emission ends (default: 1).
        :type frame_end: int
        :param lifetime: The lifetime of emitted particles in frames (default: 500000).
        :type lifetime: int
        :param random: The randomness factor for particle lifetime (default: 0).
        :type random: float
        :param emit_from: The location to emit particles from (default: 'FACE').
        :type emit_from: str
        :param use_modifier: Flag indicating whether to use modifiers (default: True).
        :type use_modifier: bool
        :param distribution: The distribution type of emitted particles (default: 'RAND').
        :type distribution: str
        :param emit_random: Flag indicating whether to use random emission (default: True).
        :type emit_random: bool
        :param even_distribution: Flag indicating whether to use even distribution (default: True).
        :type even_distribution: bool
        """
        # FEATURE: Add calculation for number of jets
        particle_settings.type = type
        particle_settings.count = count
        bpy.context.object.particle_systems["ParticleSystem"].seed = seed
        particle_settings.frame_start = frame_start
        particle_settings.frame_end = frame_end
        particle_settings.lifetime = lifetime
        particle_settings.lifetime_random = random
        particle_settings.emit_from = emit_from
        particle_settings.use_modifier_stack = use_modifier
        particle_settings.distribution = distribution
        particle_settings.use_emit_random = emit_random
        particle_settings.use_even_distribution = even_distribution

    def mod_particles_set_velocity(self, particle_settings, normal_factor=1, tangent_factor=0, tangent_phase=0,
                                   object_align_factors=(0, 0, 0), object_factor=0, factor_random=0):
        """
        Configure particle velocity settings.

        :param particle_settings: The particle settings configuration to adapt.
        :type particle_settings: bpy.types.ParticleSettings
        :param normal_factor: The factor for normal velocity (default: 1).
        :type normal_factor: float
        :param tangent_factor: The factor for tangent velocity (default: 0).
        :type tangent_factor: float
        :param tangent_phase: The phase value for tangent velocity (default: 0).
        :type tangent_phase: float
        :param object_align_factors: The factors for object-aligned velocity (default: (0, 0, 0)).
        :type object_align_factors: tuple
        :param object_factor: The factor for object velocity (default: 0).
        :type object_factor: float
        :param factor_random: The randomness factor for particle velocity (default: 0).
        :type factor_random: float
        """

        particle_settings.normal_factor = normal_factor
        particle_settings.tangent_factor = tangent_factor
        particle_settings.tangent_phase = tangent_phase
        particle_settings.object_align_factor[0] = object_align_factors[0]
        particle_settings.object_align_factor[1] = object_align_factors[1]
        particle_settings.object_align_factor[2] = object_align_factors[2]
        particle_settings.object_factor = object_factor
        particle_settings.factor_random = factor_random

    def mod_particles_set_rotation(self, particle_settings, active=False):
        """
        Configure particle rotation settings.

        :param particle_settings: The particle settings configuration to adapt
        :type particle_settings: bpy.types.particle_settings
        :param active: Flag indicating whether to enable particle rotation.
        :type active: bool
        """
        particle_settings.use_rotations = active

    def mod_particles_set_physics(self, particle_settings, type='NO'):
        """
        Configure particle physics settings.

        :param particle_settings: The particle settings configuration to adapt
        :type particle_settings: bpy.types.particle_settings
        :param type: The type of physics to apply (default: 'NO').
        :type type: str
        """
        particle_settings.physics_type = type

    def mod_particles_set_render(self, particle_settings, size=0.2, random=0.5, instance_object="Cylinder"):
        """
        Configure particle rendering settings.

        :param particle_settings: The particle settings configuration to adapt
        :type particle_settings: bpy.types.particle_settings
        :param size: The size of the rendered particles (default: 0.2).
        :type size: float
        :param random: The randomness factor for particle size (default: 0.5).
        :type random: float
        :param instance_object: The object to use for particle instancing (default: "Cylinder").
        :type instance_object: str
        """
# FEATURE: Add instance object to change from cylinder to others etc.
# FEATURE: Add parameters to json file and change to dictionary
        try:
            particle_settings.render_type = 'OBJECT'
            particle_settings.particle_size = size
            particle_settings.size_random = random
            bpy.context.object.show_instancer_for_render = True
            particle_settings.instance_object = bpy.data.objects[instance_object]
            particle_settings.use_global_instance = False
            particle_settings.use_rotation_instance = True
            particle_settings.use_scale_instance = True
            particle_settings.use_parent_particles = True
            particle_settings.show_unborn = False
            particle_settings.use_dead = False
        except KeyError as e:
            logging.warning(
                f": Should only be missing during documentation{e}")

    def mod_particles_set_viewport(self, particle_settings):
        """
        Configure particle viewport display settings.

        :param particle_settings: The particle settings configuration to adapt
        :type particle_settings: bpy.types.particle_settings
        """
        particle_settings.display_method = 'RENDER'
        particle_settings.display_color = 'MATERIAL'
        particle_settings.display_percentage = 100
        bpy.context.object.show_instancer_for_viewport = True

    def mod_particles_set_childern_interpolated(self, particle_settings, children_parting, children_clumping, children_roughness, child_type="INTERPOLATED", child_nbr=20,
                                                rendered_child_count=20, child_length=1, child_length_threshold=0,
                                                child_seed=0, virtual_parents=0, create_long_hair_children=False,
                                                ):
        """
        Configure particle children settings for the interpolated type.

        This function configures particle children settings when the child type is set to 'INTERPOLATED'.
        It sets various parameters related to the number of children, their length, seed, virtual parents, and long hair children.
        Additionally, it applies child parting, clumping, and roughness settings.

        :param particle_settings: The particle settings configuration to adapt.
        :type particle_settings: bpy.types.particle_settings
        :param children_parting: Particle child parting settings.
        :type children_parting: dict
        :param children_clumping: Particle child clumping settings.
        :type children_clumping: dict
        :param children_roughness: Particle child roughness settings.
        :type children_roughness: dict
        :param child_type: The type of particle children (default: "INTERPOLATED").
        :type child_type: str
        :param child_nbr: The number of children for each parent particle (default: 20).
        :type child_nbr: int
        :param rendered_child_count: The number of children rendered in the viewport (default: 20).
        :type rendered_child_count: int
        :param child_length: The initial length of children as a factor of the parent size (default: 1).
        :type child_length: float
        :param child_length_threshold: The threshold below which children are removed (default: 0).
        :type child_length_threshold: float
        :param child_seed: The random seed for child generation (default: 0).
        :type child_seed: int
        :param virtual_parents: The number of virtual parents for each particle (default: 0).
        :type virtual_parents: int
        :param create_long_hair_children: Whether to create long hair children (default: False).
        :type create_long_hair_children: bool
        """
        particle_settings.child_type = child_type
        particle_settings.child_nbr = child_nbr
        particle_settings.rendered_child_count = rendered_child_count
        particle_settings.child_length = child_length
        particle_settings.child_length_threshold = child_length_threshold
        bpy.context.object.particle_systems["ParticleSystem"].child_seed = child_seed
        particle_settings.virtual_parents = virtual_parents
        particle_settings.create_long_hair_children = create_long_hair_children
        self.mod_particles_set_childern_parting(particle_settings, **children_parting)
        self.mod_particles_set_childern_clumping(particle_settings, **children_clumping)
        self.mod_particles_set_childern_roughness(particle_settings, **children_roughness)
        #Kink
        particle_settings.kink = 'NO'


    def mod_particles_set_childern_parting(self, particle_settings, parting_factor = 0.529147, parting_min = 0.1, parting_max = 0):
        """
        Configure particle parting settings for children.

        :param particle_settings: The particle settings configuration to adapt.
        :type particle_settings: bpy.types.particle_settings
        :param factor: The parting factor (default: 0.529147).
        :type factor: float
        :param min: The minimum parting value (default: 0.1).
        :type min: float
        :param max: The maximum parting value (default: 0).
        :type max: float
        """
        particle_settings.child_parting_factor = parting_factor
        particle_settings.child_parting_min = parting_min
        particle_settings.child_parting_max = parting_max
        
    def mod_particles_set_childern_clumping(self, particle_settings, clump_curve = False
                                            , clump_factor = 1, clump_shape = 0, clump_noise = False):
        """
        Configure particle clumping settings for children.

        :param particle_settings: The particle settings configuration to adapt.
        :type particle_settings: bpy.types.particle_settings
        :param clump_curve: Flag indicating whether to use a clump curve (default: False).
        :type clump_curve: bool
        :param clump_factor: The clump factor (default: 1).
        :type clump_factor: float
        :param clump_shape: The clump shape (default: 0).
        :type clump_shape: int
        :param clump_noise: Flag indicating whether to use clump noise (default: False).
        :type clump_noise: bool
        """
        particle_settings.use_clump_curve = clump_curve
        particle_settings.clump_factor = clump_factor
        particle_settings.clump_shape = clump_shape
        particle_settings.use_clump_noise = clump_noise

    def mod_particles_set_childern_roughness(self, particle_settings, curve = False, one = 0, one_size = 1
                                   , endpoint = 0, end_shape = 1, two_roughness = 1, two_size = 1, 
                                   two_threshold = 0):
        """
        Configure particle roughness settings for children.

        :param particle_settings: The particle settings configuration to adapt.
        :type particle_settings: bpy.types.particle_settings
        :param curve: Flag indicating whether to use a roughness curve (default: False).
        :type curve: bool
        :param one: The roughness value for the first point on the curve (default: 0).
        :type one: float
        :param one_size: The size value for the first point on the curve (default: 1).
        :type one_size: float
        :param endpoint: The roughness value for the endpoint of the curve (default: 0).
        :type endpoint: float
        :param end_shape: The shape of the curve endpoint (default: 1).
        :type end_shape: int
        :param two_roughness: The roughness value for the second point on the curve (default: 1).
        :type two_roughness: float
        :param two_size: The size value for the second point on the curve (default: 1).
        :type two_size: float
        :param two_threshold: The threshold value for the second point on the curve (default: 0).
        :type two_threshold: float
        """
        particle_settings.use_roughness_curve = curve
        particle_settings.roughness_1 = one
        particle_settings.roughness_1_size = one_size
        particle_settings.roughness_endpoint = endpoint
        particle_settings.roughness_end_shape = end_shape
        particle_settings.roughness_2 = two_roughness
        particle_settings.roughness_2_size =two_size
        particle_settings.roughness_2_threshold = two_threshold

    def mod_particles_set_field(self, particle_settings, gravity = 0, all = 1, force = 1, vortex = 1, 
                                magnetic = 1, harmonic = 1, charge = 1, lennardjones = 1, wind = 1,
                                curve_guide = 1, texture = 1, smokeflow = 1, turbulence = 1,
                                drag = 1, boid = 1):
        """
        Configure particle field weights settings.

        :param particle_settings: The particle settings configuration to adapt.
        :type particle_settings: bpy.types.particle_settings
        :param gravity: The weight of gravity field (default: 0).
        :type gravity: float
        :param all: The weight of all fields (default: 1).
        :type all: float
        :param force: The weight of force field (default: 1).
        :type force: float
        :param vortex: The weight of vortex field (default: 1).
        :type vortex: float
        :param magnetic: The weight of magnetic field (default: 1).
        :type magnetic: float
        :param harmonic: The weight of harmonic field (default: 1).
        :type harmonic: float
        :param charge: The weight of charge field (default: 1).
        :type charge: float
        :param lennardjones: The weight of Lennard-Jones field (default: 1).
        :type lennardjones: float
        :param wind: The weight of wind field (default: 1).
        :type wind: float
        :param curve_guide: The weight of curve guide field (default: 1).
        :type curve_guide: float
        :param texture: The weight of texture field (default: 1).
        :type texture: float
        :param smokeflow: The weight of smoke flow field (default: 1).
        :type smokeflow: float
        :param turbulence: The weight of turbulence field (default: 1).
        :type turbulence: float
        :param drag: The weight of drag field (default: 1).
        :type drag: float
        :param boid: The weight of boid field (default: 1).
        :type boid: float
        """
        particle_settings.effector_weights.gravity = gravity
        particle_settings.effector_weights.all = all
        particle_settings.effector_weights.force = force
        particle_settings.effector_weights.vortex = vortex
        particle_settings.effector_weights.magnetic = magnetic
        particle_settings.effector_weights.harmonic = harmonic
        particle_settings.effector_weights.charge = charge
        particle_settings.effector_weights.lennardjones = lennardjones
        particle_settings.effector_weights.wind = wind
        particle_settings.effector_weights.curve_guide = curve_guide
        particle_settings.effector_weights.texture = texture
        particle_settings.effector_weights.smokeflow = smokeflow
        particle_settings.effector_weights.turbulence = turbulence
        particle_settings.effector_weights.drag = drag
        particle_settings.effector_weights.boid = boid

    def mod_particles_set_force(self, particle_settings, self_effect = False, amount = 0, 
                                field_1_type = 'NONE', field_2_type = 'NONE'):
        """
        Configure particle force field settings.

        :param particle_settings: The particle settings configuration to adapt.
        :type particle_settings: bpy.types.particle_settings
        :param self_effect: Flag indicating whether to enable self-effect (default: False).
        :type self_effect: bool
        :param amount: The amount of the force effect (default: 0).
        :type amount: float
        :param field_1_type: The type of the first force field (default: 'NONE').
        :type field_1_type: str
        :param field_2_type: The type of the second force field (default: 'NONE').
        :type field_2_type: str
        """
        particle_settings.use_self_effect = self_effect
        particle_settings.effector_amount = amount
        particle_settings.force_field_1.type = field_1_type
        particle_settings.force_field_2.type = field_2_type

    def particles_set_texture(self, emitter, particle_settings,texture_name = "Texture", 
                                  map_time = False, map_density = True, density_factor = 1.0, 
                                  blend_type = 'MULTIPLY' ):
        """
        Modify particle system settings to use a texture for controlling particles.

        :param emitter: The object that emits particles.
        :type emitter: bpy.types.Object
        :param particle_settings: The particle settings to modify.
        :type particle_settings: bpy.types.particle_settings
        :param texture_name: The name of the texture to use.
        :type texture_name: str
        :param map_time: Flag indicating whether to use the texture to control particle emission over time.
        :type map_time: bool
        :param map_density: Flag indicating whether to use the texture to control particle density.
        :type map_density: bool
        :param density_factor: The factor to multiply the density by when using the texture.
        :type density_factor: float
        :param blend_type: The blend type to use for combining the texture with the particle density.
        :type blend_type: str
        """
        # FEATURE: Check to add maybe multiple texture slots
        logging.info(f"Setting texture... ")
        
        try:
            texture = bpy.data.textures[texture_name]
            particle_sys = bpy.data.objects[emitter.name].particle_systems["ParticleSystem"]
            particle_sys.settings.texture_slots.add()
            particle_sys.settings.texture_slots[0].texture = texture
            particle_settings.texture_slots[0].use_map_time = map_time
            particle_settings.texture_slots[0].use_map_density = map_density
            particle_settings.texture_slots[0].density_factor = density_factor
            particle_settings.texture_slots[0].blend_type = blend_type
        except KeyError as e :
            logging.warning(f": Should only be missing during documentation{e}")


    def emitter_render_settings(self,emitter_object):
        """
        Adjust rendering settings for the emitter object.

        This function modifies various rendering-related settings of the emitter object.

        :param emitter_object: The emitter object to adjust rendering settings for.
        :type emitter_object: bpy.types.Object
        """
        # Set the emitter object as the active object
        
        logging.info(f"Defining emitter render settings...")
        bpy.context.view_layer.objects.active = emitter_object
        bpy.context.object.hide_render = False
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.use_remesh_preserve_paint_mask = False
        bpy.context.object.data.use_remesh_preserve_sculpt_face_sets = False
        bpy.context.object.data.use_remesh_preserve_vertex_colors = False
