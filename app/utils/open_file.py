import os
import platform
import subprocess
import sys


def open_file_with_dialog(file_path: str, custom_apps: dict = None):
    """
    Open a file using the OS-specific "Open With" dialog.

    On Windows: opens native "Open With..." dialog.
    On macOS: reveals the file in Finder.
    On Linux: uses xdg-open (or custom app).

    Args:
        file_path (str): The path to the file to open.
        custom_apps (dict): Optional dict of app_name -> app_executable to manually select an app.
    """
    system = platform.system()

    if not os.path.exists(file_path):
        print(f"[!] File does not exist: {file_path}")
        return

    try:
        if custom_apps:
            # If user provides custom app choices, show CLI menu
            print("Select application to open the file with:")
            for i, app in enumerate(custom_apps.keys()):
                print(f"{i + 1}. {app}")
            choice = int(input("Enter number: ")) - 1
            selected_app = list(custom_apps.values())[choice]
            subprocess.run([selected_app, file_path])
            return

        if system == "Windows":
            subprocess.run(["rundll32.exe", "shell32.dll,OpenAs_RunDLL", file_path])

        elif system == "Darwin":  # macOS
            # Let user pick app, then open file with it
            applescript = f'''
                set theFile to POSIX file "{file_path}"
                set theApp to choose application
                do shell script "open -a \\"" & POSIX path of theApp & "\\" \\"" & POSIX path of theFile & "\\""
            '''
            try:
                subprocess.run(["osascript", "-e", applescript])
            except Exception as e:
                print(f"[!] Failed to open file with selected app: {e}")

        elif system == "Linux":
            # Best effort: this opens with default app
            subprocess.run(["xdg-open", file_path])

        else:
            print(f"[!] Unsupported platform: {system}")

    except Exception as e:
        print(f"[!] Failed to open file: {e}")