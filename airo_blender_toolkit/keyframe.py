import bpy
from mathutils import Matrix

from airo_blender_toolkit.trajectory import Trajectory


def keyframe_trajectory(object: bpy.types.Object, trajectory: Trajectory, start_frame: int, end_frame: int):
    frame_range = range(start_frame, end_frame)
    for frame in frame_range:
        time_completion = float(frame - start_frame) / (len(frame_range) - 1)
        pose = trajectory.pose(time_completion)
        object.matrix_world = Matrix(pose)
        object.keyframe_insert(data_path="location", frame=frame)
        object.keyframe_insert(data_path="rotation_euler", frame=frame)
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


def is_keyframed(object, frame):
    if object.animation_data is None or object.animation_data.action is None:
        return False

    for fcurve in object.animation_data.action.fcurves:
        if frame in (int(p.co.x) for p in fcurve.keyframe_points):
            return True

    return False
