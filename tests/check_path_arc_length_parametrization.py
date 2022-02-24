import numpy as np

import airo_blender_toolkit as abt

path = abt.TiltedEllipticalArcPath(abt.Frame(np.identity(4)), [1.0, 0, 0], [0, 1.0, 0], scale=0, end_angle=180)

steps = 1000

p = path.pose(0.0).position
cumulative_distance = 0.0
path_length = path.path_length()

print(f"0.5: {path.completion_to_parameter_map[0.5]}")

print("Completion | Arc Length")

for path_completion in np.linspace(1.0 / steps, 1, steps):
    p_next = path.pose(path_completion).position
    cumulative_distance += np.linalg.norm(p_next - p)
    p = p_next
    print(f"{path_completion:.5f}     | {cumulative_distance / path_length:.5f}")


# path2 = abt.TiltedEllipticalArcPath(abt.Frame(np.identity(4)), [1.0, 0, 0], [0, 1.0, 0], end_angle=180)

for completion in np.linspace(0, 1, 11):
    abt.visualize_transform(path.pose(completion), 0.1)
    # abt.visualize_transform(path2.pose(completion), 0.1)


print(path.path_length())
