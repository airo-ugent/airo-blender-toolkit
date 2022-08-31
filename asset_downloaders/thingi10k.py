"""Downloader for the Thingi10K dataset.
Downloads the stl mesh files and converts them to tagged Blender Assets.
"""


def load_thingi10k_object():
    pass
    # thingi_folder = os.path.join(assets_path(), "thingi10k")
    # random_object_name = get_random_filename(thingi_folder)
    # print(random_object_name)
    # bpy.ops.import_mesh.stl(filepath=os.path.join(thingi_folder, random_object_name))
    # obj = bpy.context.selected_objects[0]
    # bb_vertex = obj.matrix_world @ (Vector(obj.bound_box[6]) - Vector(obj.bound_box[0]))
    # bb_vertex = [abs(x) for x in bb_vertex]
    # obj.scale = np.array([0.1 / (bb_vertex[0]), 0.1 / (bb_vertex[1]), 0.1 / (bb_vertex[2])]) * np.random.uniform(
    #     0.5, 3.0
    # )
    # obj.location = (np.random.uniform(-0.5, 0.5), np.random.uniform(-0.5, 0.5), 0)
    # material = bpy.data.materials.new(name=random_object_name)
    # material.diffuse_color = random_hsv()
    # obj.data.materials.append(material)
