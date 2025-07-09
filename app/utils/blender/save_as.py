import bpy
bpy.ops.wm.open_mainfile(filepath=r"{master_file_path}")
bpy.ops.wm.save_as_mainfile(filepath=r"{new_version_file_path}")