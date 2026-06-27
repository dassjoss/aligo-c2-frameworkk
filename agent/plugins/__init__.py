"""
Sistema de plugins para el agente ALIGO C2.
Los plugins son módulos que extienden las capacidades del agente.
"""

class BasePlugin:
    """Clase base para todos los plugins."""
    
    name = "base"
    description = "Plugin base"
    
    def run(self, args=None):
        raise NotImplementedError("El plugin debe implementar el método run()")
