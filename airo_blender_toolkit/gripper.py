import blenderproc as bproc
import bpy
import numpy as np
import trimesh

import airo_blender_toolkit as abt


def blender_obj_to_trimesh(obj):
    vertices = [np.array(obj.matrix_world @ v.co) for v in obj.data.vertices]
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


class Gripper:
    def __init__(self, gripper_obj):
        self.gripper_obj = gripper_obj
        self.grasped_vertices = None

    def action(self, grasped_obj):
        gripper_obj = self.gripper_obj
        scene = bpy.context.scene
        frame = scene.frame_current

        if not abt.is_keyframed(gripper_obj, frame):
            return {}

        if self.grasped_vertices is None:
            self.grasped_vertices = grasp(gripper_obj, grasped_obj)

        positions = {}
        for id in self.grasped_vertices:
            positions[id] = grasped_obj.matrix_world @ grasped_obj.data.vertices[id].co

        grasped_obj.parent = gripper_obj
        grasped_obj.matrix_parent_inverse = gripper_obj.matrix_world.inverted()

        scene.frame_set(frame + 1)
        positions_next = {}
        for id in self.grasped_vertices:
            positions_next[id] = grasped_obj.matrix_world @ grasped_obj.data.vertices[id].co

        grasped_obj.parent = None

        velocities = {}
        dt = 1.0 / scene.render.fps

        for id in self.grasped_vertices:
            p = positions[id]
            p_next = positions_next[id]
            v = (p_next - p) / dt
            velocities[id] = v

        scene.frame_set(frame)
        return velocities

    def action_manual(self, grasped_obj):
        gripper_obj = self.gripper_obj
        scene = bpy.context.scene
        frame = scene.frame_current

        if not abt.is_keyframed(gripper_obj, frame):
            return {}

        if self.grasped_vertices is None:
            self.grasped_vertices = grasp(gripper_obj, grasped_obj)

        pose = gripper_obj.matrix_world.copy()
        scene.frame_set(frame + 1)
        pose_next = gripper_obj.matrix_world
        transform = pose_next @ pose.inverted()

        print(transform)

        dt = 1.0 / scene.render.fps
        action = {}

        for vertex_id in self.grasped_vertices:
            position = grasped_obj.data.vertices[vertex_id].co
            position_next = transform @ position
            velocity = np.array(position_next - position) / dt
            # velocity = np.array([0, 0, 1])
            action[vertex_id] = velocity

        scene.frame_set(frame)
        return action


class BlockGripper(Gripper):
    def __init__(self, length=0.05, width=0.12, height=0.05):
        gripper = bproc.object.create_primitive("CUBE", size=1.0)
        mesh = gripper.blender_obj.data

        for v in mesh.vertices:
            v.co.x *= height
            v.co.y *= width
            v.co.z *= length

        super().__init__(gripper.blender_obj)


if __name__ == "__main__":
    gripper_obj = bpy.data.objects["Gripper"]
    grasped_obj = bpy.data.objects["Grasped"]
    grasped_vertices = grasp(gripper_obj, grasped_obj)
    print("Grasped vertices:", grasped_vertices)
    mesh = grasped_obj.data
    mesh.vertices.foreach_set("select", [i in grasped_vertices for i in range(len(mesh.vertices))])
