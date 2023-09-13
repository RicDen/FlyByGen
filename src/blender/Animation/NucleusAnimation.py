# FEATURE Create animations of the nucleus 
# angle_range = config['angle_range']
# angle_step = config['angle_step']
# def static_pose_render(angle_range, angle_step, render_name):
#     total_renders =(angle_range/angle_step)
#     current_render = 0

#     start_time = time.time()

#     for x in range(0, angle_range, angle_step):
#         for y in range(0, angle_range, angle_step):
#             for z in range(0, angle_range, angle_step):
#                 current_render+=1
#                 # Rotate the core object to the specified angles
#                 core = bpy.context.collection.objects['Core']
#                 core.rotation_euler[0] = radians(x)
#                 core.rotation_euler[1] = radians(y)
#                 core.rotation_euler[2] = radians(z)

#                 # Render the scene
#                 gen_end_time = time.time()
#                 print(f"Starting render {total_renders}/{current_render}({x}, {y}, {z})...")
#                 render(output_path, f"{render_name}_{x}_{y}_{z}")
#                 render_end_time = time.time()

#                 # Print the render time
#                 render_time = render_end_time - gen_end_time
#                 print(f"Render ({x}, {y}, {z}) took: {render_time:.2f}s")



import bpy
import math

# Clear existing mesh objects
#bpy.ops.object.select_all(action='DESELECT')
#bpy.ops.object.select_by_type(type='MESH')
##bpy.ops.object.delete()

# Add a new cube
#bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
cube = bpy.context.active_object

# Set keyframes for rotation

#cube.rotation_euler = (11, 17, 0)
rotation_duration = 100  # Number of frames for one complete rotation
for frame in range(0, rotation_duration + 1):
    angle = (frame / rotation_duration) * 2 * math.pi
    cube.rotation_euler = ((11/180)*math.pi, (17/180)*math.pi, angle)
    cube.keyframe_insert(data_path="rotation_euler", frame=frame)

# Set animation end frame
bpy.context.scene.frame_end = rotation_duration

## Render settings (optional)
#bpy.context.scene.render.image_settings.file_format = 'PNG'
#bpy.context.scene.render.filepath = "/path/to/output/folder/frame_####"
#bpy.context.scene.render.fps = 24

## Render animation
#bpy.ops.render.render(animation=True)
