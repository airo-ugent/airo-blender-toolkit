import bpy
import numpy as np
import triangle as tr

import airo_blender_toolkit as abt

object = bpy.data.objects[0]
mesh = object.data

vertices = np.array([np.array(v.co[0:2]) for v in mesh.vertices])
edges = np.array([np.array(edge.vertices) for edge in mesh.edges])

# A = dict(vertices=np.array(((0, 0), (1, 0), (1, 1), (0, 1))))
A = dict(vertices=vertices, segments=edges)
B = tr.triangulate(A, "qpa0.01")

vertices_2D = B["vertices"]
vertices_3D = np.column_stack([vertices_2D, np.zeros(vertices_2D.shape[0])])
mesh = vertices_3D, [], B["triangles"]

abt.make_object("Triangulated", mesh)
