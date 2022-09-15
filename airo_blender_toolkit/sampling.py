from typing import Callable

import numpy as np
from mathutils import Vector


def sample_point(random_point: Callable[[], Vector], condition: Callable[[Vector], bool]) -> Vector:
    """_summary_

    Args:
        random_point (Callable): The function that generates new candidate points
        condition (Callable): The function that checks whether the point is acceptable.

    Returns:
        _type_: _description_
    """
    point = random_point()
    while not condition(point):
        point = random_point()
    return point


def point_on_sphere(center: Vector = Vector.Fill(3, 0), radius: float = 1.0) -> Vector:
    point_gaussian_3D = np.random.randn(3)
    point_on_unit_sphere = point_gaussian_3D / np.linalg.norm(point_gaussian_3D)
    return radius * Vector(point_on_unit_sphere) + center
