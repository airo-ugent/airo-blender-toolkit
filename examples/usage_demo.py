import numpy as np

import airo_blender_toolkit as abt

# Creating primitives
plane = abt.Plane()
abt.Sphere()
abt.IcoSphere()

# Transforming objects
plane.location = (0.0, 0, 0, 0.5)
plane.rotation_euler = [0, np.pi / 2.0, 0.0]


# Accesing the raw Blender Object
plane.blender_object

# Cameras
camera = abt.Camera()
camera.look_at(plane.location)
camera.focal_length = 20
