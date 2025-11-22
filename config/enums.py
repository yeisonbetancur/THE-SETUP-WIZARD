from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, Any, Tuple

# ======================
# ENUMERACIONES
# ======================

class Element(Enum):
    """Elementos básicos del juego"""
    NEUTRAL = auto()
    FUEGO = auto()
    HIELO = auto()
    RAYO = auto()
    TIERRA = auto()
    AGUA = auto()

class SpellType(Enum):
    """Tipos de hechizos (básicos + combos)"""
    # Básicos (6)
    NEUTRAL = auto()
    FUEGO = auto()
    HIELO = auto()
    RAYO = auto()
    TIERRA = auto()
    AGUA = auto()
    
    # Combos duales (10)
    VAPOR = auto()              # Fuego + Hielo
    EXPLOSION = auto()          # Fuego + Rayo
    LAVA = auto()               # Fuego + Tierra
    VAPOR_CALIENTE = auto()     # Fuego + Agua
    TORMENTA_HIELO = auto()     # Hielo + Rayo
    AVALANCHA = auto()          # Hielo + Tierra
    VENTISCA = auto()           # Hielo + Agua
    TEMBLOR = auto()            # Rayo + Tierra
    ELECTROCUCION = auto()      # Rayo + Agua
    BARRO = auto()              # Tierra + Agua

class TrajectoryType(Enum):
    """Tipos de trayectoria del proyectil"""
    FRONTAL = auto()  # → Recto, rápido
    AEREA = auto()    # ↗ Arco parabólico alto
    BAJA = auto()     # ↘ Ras del suelo

class BehaviorType(Enum):
    """Comportamientos de proyectiles"""
    PROYECTIL_SIMPLE = auto()      # Va recto y desaparece al impactar
    ATRAVIESA_ENEMIGOS = auto()    # Atraviesa múltiples enemigos
    AREA_PERSISTENTE = auto()      # Se queda en el suelo haciendo daño
    PROYECTIL_MULTIPLE = auto()    # Se divide en varios proyectiles
    PROYECTIL_MASIVO = auto()      # Grande, lento pero devastador
    CADENA = auto()                # Salta entre enemigos cercanos
    ONDA_SUELO = auto()            # Propagación por el suelo
    EXPLOSION_IMPACTO = auto()     # Explota al tocar enemigo/suelo

class EffectType(Enum):
    """Efectos al impactar enemigos"""
    DAÑO_DIRECTO = auto()          # Solo hace daño
    DOT = auto()                   # Damage over time (quemadura, veneno)
    SLOW = auto()                  # Ralentiza movimiento
    STUN = auto()                  # Aturde/paraliza
    KNOCKBACK = auto()             # Empuja hacia atrás
    CONFUSION = auto()             # Confunde (enemigo cambia dirección)
    CHAIN_DAMAGE = auto()          # Daño en cadena a enemigos cercanos
    AREA_EXPLOSION = auto()        # Daño en área al impactar
    HEALING = auto()               # Cura al jugador (para algunos combos)
    FREEZE = auto()                # Congela completamente



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
