import platform
import subprocess
from pathlib import Path
from urllib.parse import urljoin
from requests.auth import HTTPBasicAuth
import requests

class MountDrive:
    def resolve_base_mount_path(self, drive_letter: str) -> Path:
        os_type = platform.system()
        drive_letter = drive_letter.upper()

        if os_type == "Windows":
            return Path(f"{drive_letter}:/")
        elif os_type == "Darwin":
            return Path(f"/Volumes/{drive_letter}")
        else:
            return Path(f"/mnt/{drive_letter}")

    def is_mounted(self, path: Path) -> bool:
        return path.exists()

    def mount_nas(self, nas_server: dict):
        proto = nas_server["protocol"]
        host = nas_server["host"]
        path = nas_server.get("remote_path", "").strip("/\\")
        username = nas_server.get("username", "")
        password = nas_server.get("password", "")
        drive_letter = nas_server.get("drive_letter", "Z").upper()
        mount_point = str(self.resolve_base_mount_path(drive_letter))

        if proto == "smb":
            # Example: //host/share -> Z:
            if platform.system() == "Windows":
                unc = f"\\\\{host}\\{path}"
                cmd = ["net", "use", f"{drive_letter}:", unc]
                if username and password:
                    cmd += [password, f"/user:{username}"]
            else:
                unc = f"//{host}/{path}"
                cmd = [
                    "mount", "-t", "cifs", unc, mount_point,
                    "-o", f"username={username},password={password},rw,vers=3.0"
                ]

        elif proto == "webdav":
            webdav_url = f"https://{host}/{path}"
            if platform.system() == "Darwin":
                cmd = ["mount_smbfs", f"//{username}:{password}@{host}/{path}", mount_point]
            else:  # Linux
                cmd = [
                    "mount", "-t", "davfs", webdav_url, mount_point,
                    "-o", f"username={username},password={password}"
                ]

        elif proto == "ftp":
            print("📡 FTP tidak perlu mount: akses via URL saja")
            return

        else:
            raise ValueError(f"Protocol '{proto}' is not supported for mounting.")

        print("🔗 Menjalankan perintah:", " ".join(cmd))
        subprocess.run(cmd, check=False)

    def get_nas_path(self, nas_server: dict, relative_path: str = "") -> str:
        proto = nas_server["protocol"]
        remote_path = nas_server.get("remote_path", "").strip("/\\")
        drive_letter = nas_server.get("drive_letter", "Z")
        host = nas_server["host"]
        username = nas_server.get("username", "")
        password = nas_server.get("password", "")

        if proto in ["smb", "webdav"]:
            base_path = self.resolve_base_mount_path(drive_letter)
            full_path = base_path / remote_path / relative_path
            if not self.is_mounted(base_path):
                self.mount_nas(nas_server)
            return str(full_path)

        elif proto == "ftp":
            return f"ftp://{username}:{password}@{host}/{remote_path}/{relative_path}"

        elif proto == "webdav":
            return f"https://{host}/{remote_path}/{relative_path}"

        elif proto == "local":
            return str(Path(remote_path) / relative_path)

        else:
            raise ValueError(f"Unsupported protocol: {proto}")