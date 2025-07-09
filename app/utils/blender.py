import os
import tempfile
import subprocess
import textwrap

class BlenderService:
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_blender_version() -> str:
        """
        Get the Blender version installed on the system.
        """
        try:
            version = os.popen('blender --version').read().strip()
            return version
        except Exception as e:
            return f"Error retrieving Blender version: {str(e)}"

    @staticmethod
    def save_as_blend_file(blender_path: str,file_path: str, target_path: str) -> dict:
        """
        Save the current Blender project as a .blend file.
        """
        try:
            blender_script_path = os.path.join(tempfile.gettempdir(), "blender_save_as.py")
            script_content = textwrap.dedent(f"""\
                        import bpy
                        bpy.ops.wm.open_mainfile(filepath=r"{file_path}")
                        bpy.ops.wm.save_as_mainfile(filepath=r"{target_path}")
                    """)

            with open(blender_script_path, "w") as f:
                f.write(script_content)

            subprocess.run([blender_path, "--background", "--python", blender_script_path])
            return {"success": True, "message": f"Project saved as {file_path}"}
        except Exception as e:
            return {"success": False, "message": f"Error saving project: {str(e)}"}