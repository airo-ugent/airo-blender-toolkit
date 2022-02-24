import bpy
from mathutils import Matrix

from airo_blender_toolkit.trajectory import Trajectory


def keyframe_trajectory(object: bpy.types.Object, trajectory: Trajectory, start_frame: int, end_frame: int):
    n_frames = (end_frame - start_frame) + 1
    for i in range(n_frames):
        time_completion = float(i) / (n_frames - 1)
        pose = trajectory.pose(time_completion)
        object.matrix_world = Matrix(pose)
        object.keyframe_insert(data_path="location", frame=i)
        object.keyframe_insert(data_path="rotation_euler", frame=i)
    object.matrix_world = Matrix(trajectory.start)
    bpy.context.view_layer.update()


def keyframe_visibility(object, start_frame, end_frame):
    object.hide_render = True
    object.hide_viewport = True
    object.keyframe_insert(data_path="hide_render", frame=max(0, start_frame - 1))
    object.keyframe_insert(data_path="hide_viewport", frame=max(0, start_frame - 1))
    object.hide_render = False
    object.hide_viewport = False
    object.keyframe_insert(data_path="hide_render", frame=start_frame)
    object.keyframe_insert(data_path="hide_viewport", frame=start_frame)
    object.keyframe_insert(data_path="hide_render", frame=end_frame)
    object.keyframe_insert(data_path="hide_viewport", frame=end_frame)
    object.hide_render = True
    object.hide_viewport = True
    object.keyframe_insert(data_path="hide_render", frame=end_frame + 1)
    object.keyframe_insert(data_path="hide_viewport", frame=end_frame + 1)
