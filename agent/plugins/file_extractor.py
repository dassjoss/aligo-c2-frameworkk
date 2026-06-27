# agent/plugins/file_extractor.py
import os
import subprocess
from plugins import BasePlugin

# Rutas de logs típicos por OS
LOG_PATHS_WINDOWS = [
    r"C:\Windows\System32\winevt\Logs",
    r"C:\Windows\Temp",
    os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp")
]

LOG_PATHS_UNIX = [
    "/var/log",
    "/tmp",
    os.path.expanduser("~")
]


class Plugin(BasePlugin):
    name = "file_extractor"
    description = "Lista logs y archivos de auditoría del sistema"

    def run(self, args=None):
        try:
            output = "=========================================\n"
            output += "      ARCHIVOS Y LOGS DE AUDITORÍA       \n"
            output += "=========================================\n"

            if os.name == 'nt':  # Windows
                for path in LOG_PATHS_WINDOWS:
                    if os.path.exists(path):
                        output += f"\n📁 {path}:\n"
                        try:
                            result = subprocess.run(
                                ['dir', path],
                                capture_output=True, text=True,
                                shell=True
                            )
                            # Mostrar solo los primeros 20 archivos
                            lines = result.stdout.split('\n')[:20]
                            output += '\n'.join(lines) + "\n"
                        except Exception as e:
                            output += f"  Error: {e}\n"
            else:  # Linux / macOS
                for path in LOG_PATHS_UNIX:
                    if os.path.exists(path):
                        output += f"\n📁 {path}:\n"
                        try:
                            result = subprocess.run(
                                ['ls', '-lah', path],
                                capture_output=True, text=True
                            )
                            lines = result.stdout.split('\n')[:20]
                            output += '\n'.join(lines) + "\n"
                        except Exception as e:
                            output += f"  Error: {e}\n"

            return output
        except Exception as e:
            return f"[-] Error en file_extractor: {str(e)}"
