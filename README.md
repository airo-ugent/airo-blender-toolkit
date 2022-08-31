# AIRO Blender Toolkit
Python package to faciliate the usage of the Blender Python API @ AIRO UGent.
The library is intended primarily for sythetic data generation and 3D visualization.

The Blender Python API consists of many operators that manipulate context data.
For example, to create cube and bevel it you would:
```python
import bpy

bpy.ops.mesh.primitive_cube_add()
cube = bpy.context.active_object
bpy.ops.editmode_toggle()
bpy.ops.mesh.bevel(offset=0.1)
bpy.ops.editmode_toggle()
```

This is useful when building a User Interface, however we believe that for developers its a bit too verbose, and an object-oriented API like this is more intuitive:
```python
import airo_blender_toolkit as abt

cube = abt.Cube()
cube.bevel(offset=0.1) # just an example, not implemented currently
```
We basically wrap the raw Blender operators and handle the context manipulation behind the scenes.

Additionally we offer many convenience functionalities on top of the Blender API, such as:

* Easy loading of assets
* Visualizations of line, axes, paths
* Find visible vertices
* Simple parametric clothes

## Installation
Requires Blender >= 3.0 to use the Asset Browser related features.

First clone this repo and then install it to your Blender python like so:

```bash
cd ~/blender-3.2.1-linux-x64/3.2/python/bin
./python3.10 -m ensurepip
./pip3 install -e ~/airo-blender-toolkit
```

## Usage

```python
import airo_blender_toolkit as abt
import numpy as np

# Creating primitives
plane = abt.Plane()
abt.Sphere()
abt.IcoSphere()

# Transforming objects
plane.location = (0.0, 0,0, 0.5)
plane.rotation_euler = [0, np.pi / 2.0, 0.0]


# Accesing the raw Blender Object
plane.blender_object

# Cameras
camera = abt.Camera()
camera.look_at(plane.location)
camera.focal_length = 20
```

Design choices:
* Our wrapper class attributes generally generally match those of the underlying classes e.g. with `object.location` and `object.rotation_euler`
* However we sometimes deviate and also remove intermediate `.data`: e.g. `camera.data.lens` became `camera.focal_length`.
