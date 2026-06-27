# agent/plugins/portscanner.py
import socket
import subprocess
import os
from plugins import BasePlugin

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143,
                443, 445, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 27017]


class Plugin(BasePlugin):
    name = "portscanner"
    description = "Escanea puertos abiertos en el sistema local"

    def run(self, args=None):
        try:
            output = "=========================================\n"
            output += "         PUERTOS ABIERTOS LOCALES        \n"
            output += "=========================================\n"

            # Método 1: netstat nativo
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    ['netstat', '-an'],
                    capture_output=True, text=True
                )
            else:  # Linux / macOS
                result = subprocess.run(
                    ['netstat', '-tuln'],
                    capture_output=True, text=True
                )

            if result.returncode == 0:
                output += result.stdout
            else:
                # Fallback: escaneo manual de puertos comunes
                output += f"{'Puerto':<10} {'Estado':<15} {'Servicio'}\n"
                output += "-" * 40 + "\n"
                
                for port in COMMON_PORTS:
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(0.3)
                        result = s.connect_ex(('127.0.0.1', port))
                        s.close()
                        if result == 0:
                            try:
                                service = socket.getservbyport(port)
                            except Exception:
                                service = "unknown"
                            output += f"{port:<10} {'ABIERTO':<15} {service}\n"
                    except Exception:
                        pass

            return output
        except Exception as e:
            return f"[-] Error en portscanner: {str(e)}"
