import numpy as np
import triangle


def triangulate(vertices, edges, minimum_triangle_density=1000.0):
    maximum_triangle_area = 1.0 / minimum_triangle_density

    input_vertices_3D = vertices
    input_vertices_2D = input_vertices_3D[:, 0:2]

    input_mesh = dict(vertices=input_vertices_2D, segments=edges)
    output_mesh = triangle.triangulate(input_mesh, f"qpa{maximum_triangle_area:.32f}")

    vertices_2D, triangles = output_mesh["vertices"], output_mesh["triangles"]
    vertices_3D = np.column_stack([vertices_2D, np.zeros(vertices_2D.shape[0])])

    mesh = vertices_3D, [], triangles
    return mesh
