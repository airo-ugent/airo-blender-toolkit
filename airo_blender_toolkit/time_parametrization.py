from abc import abstractmethod


class TimeParametrizaion:
    def __init__(self):
        pass

    @abstractmethod
    def map(self, time_completion):
        pass


class Linear(TimeParametrizaion):
    def map(self, time_completion):
        path_completion = time_completion
        return path_completion


class Bezier(TimeParametrizaion):
    def map(self, time_completion):
        # TODO do real bezier mapping
        path_completion = time_completion
        return path_completion


class MinimumJerk(TimeParametrizaion):
    def map(self, time_completion):
        t = time_completion
        return 10 * (t ** 3) - 15 * (t ** 4) + 6 * (t ** 5)
