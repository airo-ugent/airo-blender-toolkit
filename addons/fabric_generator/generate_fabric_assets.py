import argparse
import sys

import bpy
import numpy as np
from fabric_generator.generate_fabric_operator import MATERIAL_OT_generate_fabric

import airo_blender_toolkit as abt

start_seed = 0
amount = 0


def generate_next_fabric(ret):
    bpy.context.scene.fabric_seed += 1
    if bpy.context.scene.fabric_seed < start_seed + amount:
        bpy.ops.material.generate_fabric()
    else:
        finalize()


def modal_wrap(modal_func):
    def wrap(self, context, event):
        (ret,) = retset = modal_func(self, context, event)
        if ret in {"FINISHED"}:
            print(f"{self.bl_idname} returned {ret} for seed {bpy.context.scene.fabric_seed}")
            generate_next_fabric(ret)
        return retset

    return wrap


op = MATERIAL_OT_generate_fabric
op._modal_org = op.modal
op.modal = modal_wrap(op.modal)


def finalize():
    print("Finalizing.")
    print([m for m in bpy.data.materials])

    generated_materials = [m for m in bpy.data.materials if m.generated_fabric]
    n = len(generated_materials)
    columns = int(np.ceil(np.sqrt(n)))
    for i, material in enumerate(generated_materials):
        scale = 2.1
        x = scale * (i % columns)
        y = -scale * (i // columns)
        plane = abt.Plane(location=(x, y, 0))
        plane.blender_object.data.materials.append(material)

    for material in generated_materials:
        material.asset_mark()
        material.asset_data.description = "A randomly generated fabric texture."
        tags = ["fabric", "cloth", "textile", "towel", "randomized", "procedural"]
        for tag in tags:
            material.asset_data.tags.new(tag)
        material.asset_generate_preview()

    bpy.ops.file.pack_all()


if __name__ == "__main__":
    if "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1 :]  # noqa E203
        parser = argparse.ArgumentParser()
        # parser.add_argument("output_directory")
        parser.add_argument("amount", type=int)
        parser.add_argument("--start_seed", type=int, default=0)
        args = parser.parse_known_args(argv)[0]

        start_seed = int(args.start_seed)
        amount = int(args.amount)
        if amount > 0:
            print("Starting generation.")
            bpy.context.scene.fabric_seed = start_seed
            bpy.ops.material.generate_fabric()
    else:
        print("See usage instructions in README.md")
