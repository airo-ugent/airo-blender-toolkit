from setuptools import setup

# rtree is required for trimesh

setup(
    name="airo_blender_toolkit",
    author="Victor-Louis De Gusseme",
    author_email="victorlouisdg@gmail.com",
    version="0.1",
    description="Python package to faciliate the usage of the Blender python API @ AIRO UGent",
    url="https://github.com/airo-ugent/airo-blender-toolkit",
    packages=["airo_blender_toolkit"],
    install_requires=[
        "rtree",
        "triangle",
        "trimesh",
        "requests",
        "scipy",
        "pydantic",
        "appdirs",
        "pytest-blender",
    ],
)
