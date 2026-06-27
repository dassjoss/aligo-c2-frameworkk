# agent/plugins/network_enum.py
import os
import subprocess
from plugins import BasePlugin


class Plugin(BasePlugin):
    name = "network_enum"
    description = "Enumeración de interfaces de red y vecinos ARP"

    def run(self, args=None):
        try:
            if os.name == 'nt':  # Windows
                net = subprocess.run(
                    ['ipconfig', '/all'],
                    capture_output=True, text=True, check=True
                ).stdout
                arp = subprocess.run(
                    ['arp', '-a'],
                    capture_output=True, text=True, check=True
                ).stdout
            else:  # Linux / macOS
                try:
                    net = subprocess.run(
                        ['ip', 'addr'],
                        capture_output=True, text=True, check=True
                    ).stdout
                except Exception:
                    net = subprocess.run(
                        ['ifconfig'],
                        capture_output=True, text=True, check=True
                    ).stdout
                arp = subprocess.run(
                    ['arp', '-a'],
                    capture_output=True, text=True, check=True
                ).stdout

            output = "=========================================\n"
            output += "         INTERFACES DE RED (IPs)         \n"
            output += "=========================================\n"
            output += net + "\n\n"
            output += "=========================================\n"
            output += "         TABLA ARP (VECINOS DE RED)      \n"
            output += "=========================================\n"
            output += arp
            return output
        except Exception as e:
            return f"[-] Error en enumeración de red: {str(e)}"
