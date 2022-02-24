from abc import ABC, abstractmethod

import numpy as np
from scipy.spatial.transform import Rotation, Slerp

import airo_blender_toolkit as abt


class CartesianPath(ABC):
    def pose(self, path_completion):
        path_parameter = self.map(path_completion)
        return self._pose(path_parameter)

    @abstractmethod
    def _pose(self, path_parameter):
        pass

    @property
    def start(self):
        return self.pose(0.0)

    @property
    def end(self):
        return self.pose(1.0)

    def map(self, path_completion):
        path_parameter = path_completion
        return path_parameter

    def arc_length(self, segments=1000):
        total = 0.0
        for i in range(segments):
            p0 = self._pose(float(i) / segments).position
            p1 = self._pose(float(i + 1) / segments).position
            total += np.linalg.norm(p1 - p0)
        return total

    def calculate_arc_length_parametrization(self):
        for path_parameter in np.linspace(0, 1, 1000):
            self._pose(path_parameter).position
            self._pose(path_parameter + 0.001).position

    def check_arc_length_parametrization(self, segments=10):
        arc_length = self.arc_length(segments)
        total = 0.0
        print("Completion | Arc Length")
        for i in range(segments):
            p0 = self._pose(float(i) / segments).position
            p1 = self._pose(float(i + 1) / segments).position
            total += np.linalg.norm(p1 - p0)
            print(f"{float(i + 1) / segments:.3f} {total / arc_length:.3f}")


class TiltedEllipticalArcPath(CartesianPath):
    def __init__(
        self,
        start_pose,
        center,
        rotation_axis,
        start_angle=0,
        end_angle=360,
        scale=1.0,
        tilt_angle=0,
        orientation_mode="rotated",
    ):
        self._start_pose = start_pose
        self.center = np.array(center)
        self.rotation_axis = np.array(rotation_axis)
        self.start_angle = start_angle
        self.end_angle = end_angle

        self.scale = scale
        self.tilt_angle = tilt_angle

        # Get end pose as if orientation mode was "rotated", only used internally
        self.orientation_mode = "rotated"
        self._end_pose = self.end
        self.orientation_mode = orientation_mode

    def _rotation_basis(self):
        X = self.rotation_axis
        X /= np.linalg.norm(X)

        start = self._start_pose.position
        projection = abt.project_point_on_line(start, self.center, X)
        Y = start - projection
        Y /= np.linalg.norm(Y)

        Z = np.cross(X, Y)
        return abt.Frame.from_vectors(X, Y, Z, projection)

    def _pose(self, path_parameter=0.5):
        """Get a pose along the path at a given completion.

        Args:
            path_parameter (float): fraction of the arc to complete

        Returns:
            np.ndarray: a 4x4 matrix that describes a 3D pose
        """
        angle = self.start_angle + path_parameter * (self.end_angle - self.start_angle)
        basis = self._rotation_basis()

        rotation_matrix = np.identity(4)
        rotation_matrix[:3, :3] = Rotation.from_rotvec([angle, 0, 0], degrees=True).as_matrix()

        tilt_matrix = np.identity(4)
        tilt_matrix[:3, :3] = Rotation.from_rotvec(np.array([0, self.tilt_angle, 0]), degrees=True).as_matrix()

        P = self._start_pose.copy()
        P = np.linalg.inv(basis) @ P
        P = rotation_matrix @ P
        P[2, 3] *= self.scale
        P[:, 3] = tilt_matrix @ P[:, 3]  # Only tilt position, not orientation
        P = basis @ P
        pose = P

        if self.orientation_mode == "constant":
            pose[:3, :3] = self._start_pose.orientation

        elif self.orientation_mode == "slerp":
            orientations = Rotation.from_matrix([self._start_pose.orientation, self._end_pose.orientation])
            slerp = Slerp([0.0, 1.0], orientations)
            interpolated_orientation = slerp(path_parameter).as_matrix()
            pose[:3, :3] = interpolated_orientation

        return abt.Frame(pose)


class CircularArcPath(TiltedEllipticalArcPath):
    def __init__(
        self,
        start_pose,
        center,
        rotation_axis,
        start_angle=0,
        end_angle=360,
        orientation_mode="rotated",
    ):
        scale = 1.0
        tilt_angle = 0
        super.__init__(start_pose, center, rotation_axis, start_angle, end_angle, scale, tilt_angle, orientation_mode)


class EllipticalArcPath(TiltedEllipticalArcPath):
    def __init__(
        self,
        start_pose,
        center,
        rotation_axis,
        start_angle=0,
        end_angle=360,
        scale=1.0,
        orientation_mode="rotated",
    ):
        tilt_angle = 0
        super.__init__(start_pose, center, rotation_axis, start_angle, end_angle, scale, tilt_angle, orientation_mode)
