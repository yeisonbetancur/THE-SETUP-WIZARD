from dataclasses import dataclass, field
from typing import Dict, Any, Tuple
from enums import BehaviorType
from enums import EffectType


@dataclass
class SpellData:
    """Configuración completa de un hechizo"""
    nombre: str
    color_primario: Tuple[int, int, int]
    color_secundario: Tuple[int, int, int] = None  # Para combos
    velocidad: float = 400.0
    daño: int = 10
    tamaño: int = 10  # Radio del proyectil
    duracion: float = 5.0  # Tiempo de vida máximo
    comportamiento: BehaviorType = BehaviorType.PROYECTIL_SIMPLE
    efecto: EffectType = EffectType.DAÑO_DIRECTO
    efecto_params: Dict[str, Any] = field(default_factory=dict)
    
    # Modificadores de trayectoria
    gravedad: float = 0.0  # Para trayectorias aéreas
    friccion: float = 0.0  # Para proyectiles en suelo

# ======================
# BASE DE DATOS DE HECHIZOS
# ======================
