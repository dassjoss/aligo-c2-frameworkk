# agent/plugins/process_list.py
import os
import subprocess
from plugins import BasePlugin


class Plugin(BasePlugin):
    name = "process_list"
    description = "Lista todos los procesos en ejecución del sistema"

    def run(self, args=None):
        try:
            output = "=========================================\n"
            output += "         PROCESOS EN EJECUCIÓN           \n"
            output += "=========================================\n"

            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    ['tasklist'],
                    capture_output=True, text=True, check=True
                )
            else:  # Linux / macOS
                result = subprocess.run(
                    ['ps', 'aux'],
                    capture_output=True, text=True, check=True
                )

            output += result.stdout
            return output
        except Exception as e:
            return f"[-] Error al listar procesos: {str(e)}"
