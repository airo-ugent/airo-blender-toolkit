import numpy as np
from mathutils import Color

# AIRO color palette
light_blue = [0.693872, 0.775822, 0.822786, 1.000000]
dark_green = [0.147027, 0.479320, 0.391573, 1.000000]
orange = [0.947307, 0.597202, 0.208637, 1.000000]
red = [0.564712, 0.078187, 0.090842, 1.000000]


def random_hsv(hrange=(0.0, 1.0), srange=(0.0, 1.0), vrange=(0.0, 1.0)):
    color = Color()
    cloth_hue = np.random.uniform(*hrange)
    cloth_saturation = np.random.uniform(*srange)
    cloth_value = np.random.uniform(*vrange)
    color.hsv = cloth_hue, cloth_saturation, cloth_value
    return tuple(color) + (1,)
