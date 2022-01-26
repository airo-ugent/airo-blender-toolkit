from mathutils import Vector


# TODO cleanup and document
def look_at(point, camera):
    direction = Vector(point) - camera.location
    rot_quat = direction.to_track_quat("-Z", "Y")
    camera.rotation_euler = rot_quat.to_euler()
