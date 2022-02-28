from airo_blender_toolkit.time_parametrization import Linear


class Trajectory:
    def __init__(self, path, time_parametrization=Linear(), early_stop=1.0):
        self.path = path
        self.time_parametrization = time_parametrization

    @property
    def start(self):
        return self.pose(0.0)

    @property
    def end(self):
        return self.pose(1.0)

    def pose(self, time_completion):
        path_completion = self.time_parametrization.map(time_completion)
        return self.path.pose(path_completion)
