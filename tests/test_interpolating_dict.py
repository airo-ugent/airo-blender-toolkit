from airo_blender_toolkit.datastructures import InterpolatingDict

d = InterpolatingDict()
d[0.0] = 0.0
d[1.0] = 2.0

print(f"{d[0.5]} should be 1.0")
