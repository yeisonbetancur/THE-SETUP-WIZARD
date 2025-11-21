from typing import Dict, Any, Tuple

from config.enums import BehaviorType
from config.enums import EffectType
from config.enums import SpellType
from config.enums import Element
from config.dataclass import SpellData

SPELL_DATABASE: Dict[SpellType, SpellData] = {
    # ==================
    # HECHIZOS BÁSICOS
    # ==================
    
    SpellType.NEUTRAL: SpellData(
        nombre="Proyectil Mágico",
        color_primario=(200, 200, 200),
        velocidad=400,
        daño=10,
        tamaño=8,
        comportamiento=BehaviorType.PROYECTIL_SIMPLE,
        efecto=EffectType.DAÑO_DIRECTO
    ),
    
    SpellType.FUEGO: SpellData(
        nombre="Bola de Fuego",
        color_primario=(255, 100, 50),
        color_secundario=(255, 200, 0),
        velocidad=450,
        daño=15,
        tamaño=25,
        comportamiento=BehaviorType.PROYECTIL_SIMPLE,
        efecto=EffectType.DOT,
        efecto_params={
            "duracion": 3.0,      # Quema por 3 segundos
            "tick_damage": 2,     # 2 de daño por tick
            "tick_rate": 0.5      # Cada 0.5 segundos
        }
    ),
    
    SpellType.HIELO: SpellData(
        nombre="Orbe de Hielo",
        color_primario=(100, 200, 255),
        color_secundario=(200, 240, 255),
        velocidad=350,
        daño=12,
        tamaño=10,
        comportamiento=BehaviorType.PROYECTIL_SIMPLE,
        efecto=EffectType.SLOW,
        efecto_params={
            "slow_factor": 0.5,   # Reduce velocidad al 50%
            "duracion": 2.0       # Ralentiza por 2 segundos
        }
    ),
    
    SpellType.RAYO: SpellData(
        nombre="Rayo",
        color_primario=(255, 255, 100),
        color_secundario=(255, 255, 200),
        velocidad=600,
        daño=10,
        tamaño=6,
        comportamiento=BehaviorType.ATRAVIESA_ENEMIGOS,
        efecto=EffectType.DAÑO_DIRECTO,
        efecto_params={
            "max_enemigos": 3     # Puede atravesar 3 enemigos
        }
    ),
    
    SpellType.TIERRA: SpellData(
        nombre="Roca",
        color_primario=(139, 90, 43),
        color_secundario=(100, 70, 30),
        velocidad=300,
        daño=20,
        tamaño=14,
        comportamiento=BehaviorType.PROYECTIL_SIMPLE,
        efecto=EffectType.STUN,
        efecto_params={
            "duracion": 1.5       # Aturde por 1.5 segundos
        }
    ),
    
    SpellType.AGUA: SpellData(
        nombre="Onda de Agua",
        color_primario=(50, 100, 255),
        color_secundario=(100, 150, 255),
        velocidad=380,
        daño=8,
        tamaño=12,
        comportamiento=BehaviorType.PROYECTIL_SIMPLE,
        efecto=EffectType.KNOCKBACK,
        efecto_params={
            "fuerza": 200         # Fuerza del empujón
        }
    ),
    
    # ==================
    # COMBOS DUALES
    # ==================
    
    SpellType.VAPOR: SpellData(
        nombre="Vapor",
        color_primario=(180, 180, 220),
        color_secundario=(200, 150, 150),
        velocidad=250,
        daño=10,
        tamaño=25,
        duracion=4.0,
        comportamiento=BehaviorType.AREA_PERSISTENTE,
        efecto=EffectType.CONFUSION,
        efecto_params={
            "duracion": 4.0,      # Nube dura 4 segundos
            "radio": 80           # Radio de la nube
        }
    ),
    
    SpellType.EXPLOSION: SpellData(
        nombre="Explosión",
        color_primario=(255, 150, 0),
        color_secundario=(255, 255, 100),
        velocidad=500,
        daño=25,
        tamaño=10,
        comportamiento=BehaviorType.EXPLOSION_IMPACTO,
        efecto=EffectType.AREA_EXPLOSION,
        efecto_params={
            "radio_explosion": 100,    # Radio de la explosión
            "daño_centro": 25,         # Daño en el centro
            "daño_borde": 10           # Daño en el borde
        }
    ),
    
    SpellType.LAVA: SpellData(
        nombre="Lava",
        color_primario=(255, 80, 0),
        color_secundario=(200, 50, 0),
        velocidad=300,
        daño=8,
        tamaño=20,
        duracion=6.0,
        comportamiento=BehaviorType.AREA_PERSISTENTE,
        efecto=EffectType.DOT,
        efecto_params={
            "duracion": 6.0,      # Lava persiste 6 segundos
            "tick_damage": 5,     # 5 de daño por tick
            "tick_rate": 0.3,     # Cada 0.3 segundos
            "radio": 50           # Radio del charco de lava
        }
    ),
    
    SpellType.VAPOR_CALIENTE: SpellData(
        nombre="Vapor Curativo",
        color_primario=(255, 200, 200),
        color_secundario=(255, 150, 150),
        velocidad=200,
        daño=5,
        tamaño=30,
        duracion=5.0,
        comportamiento=BehaviorType.AREA_PERSISTENTE,
        efecto=EffectType.HEALING,
        efecto_params={
            "duracion": 5.0,      # Nube dura 5 segundos
            "heal_tick": 3,       # Cura 3 HP por tick
            "tick_rate": 0.5,     # Cada 0.5 segundos
            "radio": 60           # Radio de curación
        }
    ),
    
    SpellType.TORMENTA_HIELO: SpellData(
        nombre="Tormenta de Hielo",
        color_primario=(150, 220, 255),
        color_secundario=(100, 180, 255),
        velocidad=1000,
        daño=8,
        tamaño=20,
        comportamiento=BehaviorType.PROYECTIL_MULTIPLE,
        efecto=EffectType.FREEZE,
        efecto_params={
            "num_proyectiles": 8,      # Dispara 5 proyectiles
            "spread_angulo": 85,       # Ángulo de dispersión
            "duracion_congelacion": 2.0
        }
    ),
    
    SpellType.AVALANCHA: SpellData(
        nombre="Avalancha",
        color_primario=(200, 220, 240),
        color_secundario=(150, 170, 190),
        velocidad=700,
        daño=35,
        tamaño=30,
        comportamiento=BehaviorType.PROYECTIL_MASIVO,
        efecto=EffectType.STUN,
        efecto_params={
            "duracion": 3.0,      # Aturde por 3 segundos
            "empuje": 300         # También empuja
        }
    ),
    
    SpellType.VENTISCA: SpellData(
        nombre="Ventisca",
        color_primario=(100, 180, 255),
        color_secundario=(150, 220, 255),
        velocidad=280,
        daño=12,
        tamaño=40,
        duracion=3.0,
        comportamiento=BehaviorType.ONDA_SUELO,
        efecto=EffectType.SLOW,
        efecto_params={
            "slow_factor": 0.3,   # Reduce velocidad al 30%
            "duracion": 3.0,      # Ralentiza por 3 segundos
            "ancho_onda": 150     # Ancho de la onda
        }
    ),
    
    SpellType.TEMBLOR: SpellData(
        nombre="Temblor",
        color_primario=(180, 140, 80),
        color_secundario=(220, 200, 100),
        velocidad=350,
        daño=15,
        tamaño=20,
        comportamiento=BehaviorType.ONDA_SUELO,
        efecto=EffectType.STUN,
        efecto_params={
            "duracion": 1.0,      # Aturde por 1 segundo
            "ondas": 3,           # Crea 3 ondas sísmicas
            "separacion": 50      # Separación entre ondas
        }
    ),
    
    SpellType.ELECTROCUCION: SpellData(
        nombre="Electrocución",
        color_primario=(100, 200, 255),
        color_secundario=(255, 255, 150),
        velocidad=500,
        daño=12,
        tamaño=10,
        comportamiento=BehaviorType.CADENA,
        efecto=EffectType.CHAIN_DAMAGE,
        efecto_params={
            "max_saltos": 4,           # Salta a 4 enemigos
            "rango_salto": 150,        # Rango máximo de salto
            "reduccion_daño": 0.8      # Cada salto hace 80% del anterior
        }
    ),
    
    SpellType.BARRO: SpellData(
        nombre="Barro",
        color_primario=(120, 90, 60),
        color_secundario=(80, 60, 40),
        velocidad=250,
        daño=10,
        tamaño=18,
        duracion=4.0,
        comportamiento=BehaviorType.AREA_PERSISTENTE,
        efecto=EffectType.SLOW,
        efecto_params={
            "slow_factor": 0.2,   # Reduce velocidad al 20%
            "duracion": 4.0,      # Ralentiza por 4 segundos
            "radio": 70           # Radio del charco
        }
    ),
}

# ======================
# TABLA DE COMBINACIONES
# ======================

COMBO_TABLE: Dict[frozenset, SpellType] = {
    frozenset([Element.FUEGO, Element.HIELO]): SpellType.VAPOR,
    frozenset([Element.FUEGO, Element.RAYO]): SpellType.EXPLOSION,
    frozenset([Element.FUEGO, Element.TIERRA]): SpellType.LAVA,
    frozenset([Element.FUEGO, Element.AGUA]): SpellType.VAPOR_CALIENTE,
    frozenset([Element.HIELO, Element.RAYO]): SpellType.TORMENTA_HIELO,
    frozenset([Element.HIELO, Element.TIERRA]): SpellType.AVALANCHA,
    frozenset([Element.HIELO, Element.AGUA]): SpellType.VENTISCA,
    frozenset([Element.RAYO, Element.TIERRA]): SpellType.TEMBLOR,
    frozenset([Element.RAYO, Element.AGUA]): SpellType.ELECTROCUCION,
    frozenset([Element.TIERRA, Element.AGUA]): SpellType.BARRO,
}

# ======================
# MAPEO ELEMENTO → SPELL BÁSICO
# ======================

ELEMENT_TO_SPELL: Dict[Element, SpellType] = {
    Element.NEUTRAL: SpellType.NEUTRAL,
    Element.FUEGO: SpellType.FUEGO,
    Element.HIELO: SpellType.HIELO,
    Element.RAYO: SpellType.RAYO,
    Element.TIERRA: SpellType.TIERRA,
    Element.AGUA: SpellType.AGUA,
}

# ======================
# FUNCIONES DE UTILIDAD
# ======================

def get_spell_data(spell_type: SpellType) -> SpellData:
    """Obtiene los datos de un hechizo"""
    return SPELL_DATABASE[spell_type]

def elemento_a_spell_basico(elemento: Element) -> SpellType:
    """Convierte un elemento en su hechizo básico correspondiente"""
    return ELEMENT_TO_SPELL[elemento]

def buscar_combo(elem1: Element, elem2: Element) -> SpellType:
    """
    Busca si existe un combo entre dos elementos.
    Retorna el SpellType del combo o None si no existe.
    """
    combo_key = frozenset([elem1, elem2])
    return COMBO_TABLE.get(combo_key, None)