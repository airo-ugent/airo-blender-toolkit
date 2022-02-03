import numpy as np
from scipy.spatial.transform import Rotation


def rotate_vertex(v, rotation_origin, rotation_axis, angle):
    unit_axis = rotation_axis / np.linalg.norm(rotation_axis)
    r = Rotation.from_rotvec(angle * unit_axis)
    v_new = r.as_matrix() @ (v - rotation_origin) + rotation_origin
    return v_new
