import os
import re

class VersionShotService:
    @staticmethod
    def get_version_shot_data(folder_path: str):
        """
        Scans the folder and separates normal files from autosave/backup files.

        Returns:
            normal_files: dict[int, dict[str, str]]  # version -> {file_name: full_path}
            backup_files: dict[int, dict[str, str]]
        """
        try:
            if not os.path.isdir(folder_path):
                print(f"[!] Not a valid directory: {folder_path}")
                return {}, {}

            files = os.listdir(folder_path)
            normal_files = {}
            backup_files = {}

            version_regex = re.compile(r"_v(\d{3,})", re.IGNORECASE)

            for file in files:
                full_path = os.path.join(folder_path, file)
                if not os.path.isfile(full_path):
                    continue

                _, ext = os.path.splitext(file)

                # Determine if it's a backup (e.g., .blend1, .blend2)
                is_backup = False
                if not ext or not ext[1:].isalpha():  # .blend1, .blend2
                    is_backup = True

                # Extract version number
                match = version_regex.search(file)
                version = int(match.group(1)) if match else 0

                target_dict = backup_files if is_backup else normal_files
                if version not in target_dict:
                    target_dict[version] = {}
                target_dict[version][file] = full_path

            # Optional: Sort version keys
            normal_files = dict(sorted(normal_files.items()))
            backup_files = dict(sorted(backup_files.items()))

            return normal_files, backup_files

        except Exception as e:
            print(f"[-] Error getting version shot data: {e}")
            return {}, {}
