# agent/plugins/sysinfo.py
import os
import platform
import subprocess
from plugins import BasePlugin


class Plugin(BasePlugin):
    name = "sysinfo"
    description = "Auditoría básica de hardware y sistema operativo"

    def run(self, args=None):
        try:
            output = "=========================================\n"
            output += "         INFORMACIÓN DEL SISTEMA         \n"
            output += "=========================================\n"
            output += f"OS:           {platform.system()} {platform.release()}\n"
            output += f"Version:      {platform.version()}\n"
            output += f"Arquitectura: {platform.machine()}\n"
            output += f"Hostname:     {platform.node()}\n"
            output += f"Procesador:   {platform.processor()}\n"
            output += f"Python:       {platform.python_version()}\n"
            output += f"Usuario:      {os.getenv('USERNAME') or os.getenv('USER') or 'unknown'}\n"

            if os.name == 'nt':  # Windows
                # CPU y RAM via wmic
                cpu = subprocess.run(
                    ['wmic', 'cpu', 'get', 'Name'],
                    capture_output=True, text=True
                ).stdout.strip().split('\n')[-1].strip()
                
                ram = subprocess.run(
                    ['wmic', 'computersystem', 'get', 'TotalPhysicalMemory'],
                    capture_output=True, text=True
                ).stdout.strip().split('\n')[-1].strip()
                
                ram_gb = round(int(ram) / (1024**3), 2) if ram.isdigit() else "N/A"
                output += f"CPU:          {cpu}\n"
                output += f"RAM Total:    {ram_gb} GB\n"
            else:  # Linux / macOS
                try:
                    with open('/proc/meminfo', 'r') as f:
                        for line in f:
                            if 'MemTotal' in line:
                                ram_kb = int(line.split()[1])
                                output += f"RAM Total:    {round(ram_kb / (1024**2), 2)} GB\n"
                                break
                except Exception:
                    pass

            return output
        except Exception as e:
            return f"[-] Error en sysinfo: {str(e)}"
