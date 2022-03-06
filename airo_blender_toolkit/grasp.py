import bpy
import numpy as np
import trimesh


def blender_obj_to_trimesh(obj):
    vertices = [np.array(v.co) for v in obj.data.vertices]
    faces = [np.array(poly.vertices) for poly in obj.data.polygons]
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=False)


def grasp(gripper_obj, grasped_obj):
    """Returns of set of vertex ids of the vertices of grasped_obj that are grasped by the gripper.
    A vertex is grasped if it is part of a triangle of which any vertices is grasped.

    Warning: currently only works if grasped_obj is a clean triangle mesh in Blender.
    """

    gripper = blender_obj_to_trimesh(gripper_obj)
    grasped = blender_obj_to_trimesh(grasped_obj)

    grasped_vertices = set()

    for face in grasped.faces:
        face_vertices_inside_gripper = gripper.contains(grasped.vertices[face])
        if any(face_vertices_inside_gripper):
            grasped_vertices = grasped_vertices.union(face)

    return grasped_vertices


if __name__ == "__main__":
    gripper_obj = bpy.data.objects["Gripper"]
    grasped_obj = bpy.data.objects["Grasped"]
    grasped_vertices = grasp(gripper_obj, grasped_obj)

    # for v in grasped_obj.data.vertices:
    #     if v.index in grasped_vertices:
    #         v.select_set(True)
    #     else:
    #         v.select_set(False)

    print(grasped_vertices)

    mesh = grasped_obj.data
    mesh.vertices.foreach_set("select", [i in grasped_vertices for i in range(len(mesh.vertices))])
