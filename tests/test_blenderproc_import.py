import os

os.environ["INSIDE_OF_THE_INTERNAL_BLENDER_PYTHON_ENVIRONMENT"] = "1"
import blenderproc as bproc  # noqa: E402

bproc.init()
