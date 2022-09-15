from airo_blender_toolkit.datastructures import InterpolatingDict


def test_interpotations():
    d = InterpolatingDict()
    d[0.0] = 0.0
    d[1.0] = 2.0
    assert d[0.5] == 1.0
    assert d[0.25] == 0.5
    assert d[1.0 / 3] == 2.0 / 3
