import airo_blender_toolkit as abt


def test_triangulate_plane():
    plane = abt.Plane()
    plane.triangulate(minimum_triangle_density=100.0)


if __name__ == "__main__":
    abt.clear_scene()
    test_triangulate_plane()
