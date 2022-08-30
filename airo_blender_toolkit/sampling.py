import numpy as np


def point_on_sphere(center=(0, 0, 0), radius=1.0):
    point = np.random.randn(3)
    point /= np.linalg.norm(point)
    return point
