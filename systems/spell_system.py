import pygame
from typing import Optional, Tuple
import math

from config.enums import SpellType, BehaviorType, TrajectoryType
from config.spell_data import get_spell_data
from systems.projectile import ProjectilePool, Projectile
from systems.area_effect import AreaEffectPool, AreaEffect


class SpellSystem:
    """
    Sistema central que gestiona el lanzamiento de hechizos.
    Decide si crear un proyectil o un efecto de área según el BehaviorType.
    """
    
    def __init__(self, projectile_pool_size: int = 50, area_pool_size: int = 30):
        """
        Args:
            projectile_pool_size: Tamaño del pool de proyectiles
            area_pool_size: Tamaño del pool de efectos de área
        """
        self.projectile_pool = ProjectilePool(projectile_pool_size)
        self.area_pool = AreaEffectPool(area_pool_size)
        
        # Mapeo de behaviors a tipo de spawn
        self.projectile_behaviors = {
            BehaviorType.PROYECTIL_SIMPLE,
            BehaviorType.ATRAVIESA_ENEMIGOS,
            BehaviorType.PROYECTIL_MULTIPLE,
            BehaviorType.PROYECTIL_MASIVO,
            BehaviorType.CADENA,
            BehaviorType.EXPLOSION_IMPACTO
        }
        
        self.area_behaviors = {
            BehaviorType.AREA_PERSISTENTE,
            BehaviorType.ONDA_SUELO
        }
    
    def cast_spell(self, spell_type: SpellType, player_x: float, player_y: float) -> bool:
        """
        Lanza un hechizo desde la posición del jugador.
        
        Args:
            spell_type: Tipo de hechizo a lanzar
            player_x: Posición X del jugador
            player_y: Posición Y del jugador
            
        Returns:
            True si el hechizo fue lanzado exitosamente, False si falló
        """
        spell_data = get_spell_data(spell_type)
        behavior = spell_data.comportamiento
        
        # Decidir qué tipo de entidad crear
        if behavior in self.projectile_behaviors:
            return self._cast_projectile(spell_type, player_x, player_y, spell_data)
        elif behavior in self.area_behaviors:
            return self._cast_area_effect(spell_type, spell_data)
        else:
            print(f"WARNING: Behavior {behavior} no implementado")
            return False
    
    def _cast_projectile(self, spell_type: SpellType, player_x: float, 
                         player_y: float, spell_data) -> bool:
        """Crea uno o más proyectiles según el hechizo"""
        
        # Obtener trayectoria del hechizo (asumiendo que está en spell_data)
        # TODO: Agregar campo 'trayectoria' a SpellData
        trajectory = self._get_trajectory_for_spell(spell_type)
        
        # Casos especiales
        if spell_data.comportamiento == BehaviorType.PROYECTIL_MULTIPLE:
            return self._cast_multiple_projectiles(spell_type, player_x, player_y, 
                                                   trajectory, spell_data)
        
        # Proyectil simple/normal
        offset_x = 50  # Distancia desde el jugador
        start_x = player_x + offset_x
        start_y = player_y
        
        projectile = self.projectile_pool.spawn(spell_type, start_x, start_y, trajectory)
        return projectile is not None
    
    def _cast_multiple_projectiles(self, spell_type: SpellType, player_x: float,
                                   player_y: float, trajectory: TrajectoryType, 
                                   spell_data) -> bool:
        """Lanza múltiples proyectiles en spread (ej: Tormenta de Hielo)"""
        num_proyectiles = spell_data.efecto_params.get("num_proyectiles", 3)
        spread_angulo = spell_data.efecto_params.get("spread_angulo", 20)
        
        offset_x = 50
        start_x = player_x + offset_x
        start_y = player_y
        trajectory=spell_type.trajectory
        
        # Calcular ángulos de dispersión
        if num_proyectiles == 1:
            angles = [0]
        else:
            step = spread_angulo / (num_proyectiles - 1)
            angles = [i * step - spread_angulo/2 for i in range(num_proyectiles)]
        
        success_count = 0
        for angle in angles:
            projectile = self.projectile_pool.spawn(spell_type, start_x, start_y, trajectory)
            if projectile:
                # Modificar velocidad para el spread
                self._apply_spread_to_projectile(projectile, angle)
                success_count += 1
        
        return success_count > 0
    
    def _apply_spread_to_projectile(self, projectile: Projectile, angle_degrees: float):
        """Aplica un ángulo de spread a la velocidad del proyectil"""
        angle_rad = math.radians(angle_degrees)
        
        # Rotar vector de velocidad
        vx = projectile.state.vx
        vy = projectile.state.vy
        
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        projectile.state.vx = vx * cos_a - vy * sin_a
        projectile.state.vy = vx * sin_a + vy * cos_a
    
    def _cast_area_effect(self, spell_type: SpellType, spell_data) -> bool:
        """Crea un efecto de área en el centro de la pantalla (ras del suelo)"""
        effect = self.area_pool.spawn_ground_center(spell_type)
        return effect is not None
    
    def _get_trajectory_for_spell(self, spell_type: SpellType) -> TrajectoryType:
        """
        Determina la trayectoria para un hechizo.
        TODO: Esto debería venir de SpellData cuando se agregue el campo 'trayectoria'
        
        Por ahora, hardcodeamos algunas trayectorias lógicas:
        """
        # Mapeo temporal (hasta que agregues el campo a SpellData)
        trajectory_map = {
            SpellType.NEUTRAL: TrajectoryType.FRONTAL,
            SpellType.FUEGO: TrajectoryType.FRONTAL,
            SpellType.HIELO: TrajectoryType.AEREA,
            SpellType.RAYO: TrajectoryType.FRONTAL,
            SpellType.TIERRA: TrajectoryType.BAJA,
            SpellType.AGUA: TrajectoryType.FRONTAL,
            
            # Combos
            SpellType.EXPLOSION: TrajectoryType.FRONTAL,
            SpellType.TORMENTA_HIELO: TrajectoryType.AEREA,
            SpellType.AVALANCHA: TrajectoryType.AEREA,
            SpellType.ELECTROCUCION: TrajectoryType.FRONTAL,
        }
        
        return trajectory_map.get(spell_type, TrajectoryType.FRONTAL)
    
    def update(self, dt: float):
        """Actualiza todos los proyectiles y efectos de área"""
        self.projectile_pool.update(dt)
        self.area_pool.update(dt)
    
    def draw(self, screen: pygame.Surface):
        """Dibuja todos los proyectiles y efectos de área"""
        # Dibujar efectos de área primero (debajo de los proyectiles)
        self.area_pool.draw(screen)
        self.projectile_pool.draw(screen)
    
    def get_active_projectiles(self):
        """Retorna proyectiles activos para sistema de colisiones"""
        return self.projectile_pool.get_active_projectiles()
    
    def get_active_area_effects(self):
        """Retorna efectos de área activos para sistema de colisiones"""
        return self.area_pool.get_active_effects()
    
    def clear_all(self):
        """Limpia todos los hechizos activos (útil al cambiar oleada/perder vida)"""
        self.projectile_pool.clear_all()
        self.area_pool.clear_all()
    
    def get_stats(self) -> dict:
        """Retorna estadísticas de ambos pools (para debug)"""
        return {
            "projectiles": self.projectile_pool.get_stats(),
            "area_effects": self.area_pool.get_stats()
        }
    


# ======================
# EJEMPLO DE USO
# ======================

"""
# En tu PlayingState o donde manejes el juego:

def __init__(self):
    self.spell_system = SpellSystem(projectile_pool_size=50, area_pool_size=30)
    self.player_x = 100
    self.player_y = 600

def on_gesture_detected(self, gesture_type):
    if gesture_type == "FIST":  # Lanzar hechizo
        # Determinar qué hechizo lanzar según círculos activos
        spell_type = self.determine_spell_from_circles()
        self.spell_system.cast_spell(spell_type, self.player_x, self.player_y)

def update(self, dt):
    self.spell_system.update(dt)
    
    # Luego hacer colisiones con enemigos
    for projectile in self.spell_system.get_active_projectiles():
        for enemy in self.enemies:
            if projectile.rect.colliderect(enemy.rect):
                # Aplicar daño, efectos, etc.
                ...

def draw(self, screen):
    self.spell_system.draw(screen)
"""