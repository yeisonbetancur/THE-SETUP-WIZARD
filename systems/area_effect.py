import pygame
from typing import List, Optional, Set
from dataclasses import dataclass, field

from config.enums import SpellType, EffectType
from config.spell_data import get_spell_data, SpellData


@dataclass
class AreaEffectState:
    """Estado interno de un efecto de área"""
    active: bool = False
    x: float = 0.0
    y: float = 0.0
    lifetime: float = 0.0
    tick_timer: float = 0.0
    spell_data: Optional[SpellData] = None
    affected_enemies: Set[int] = field(default_factory=set)  # IDs de enemigos afectados


class AreaEffect:
    """
    Efecto de área estático que persiste en una zona.
    Ejemplos: Lava, Vapor, Barro, Temblor, etc.
    """
    
    # Constantes de pantalla
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    
    def __init__(self):
        self.state = AreaEffectState()
        self.rect = pygame.Rect(0, 0, 100, 100)  # Área de efecto
        
    def activate(self, spell_type: SpellType, center_x: float, center_y: float):
        """Activa el efecto de área en una posición específica"""
        self.state.active = True
        self.state.spell_data = get_spell_data(spell_type)
        self.state.x = center_x
        self.state.y = center_y
        self.state.lifetime = 0.0
        self.state.tick_timer = 0.0
        self.state.affected_enemies.clear()
        
        # Configurar área de efecto según radio
        radius = self.state.spell_data.efecto_params.get("radio", 50)
        self._update_rect(radius)
        
    def _update_rect(self, radius: float):
        """Actualiza el rectángulo de colisión del área"""
        size = int(radius * 2)
        self.rect.x = int(self.state.x - radius)
        self.rect.y = int(self.state.y - radius)
        self.rect.width = size
        self.rect.height = size
    
    def update(self, dt: float) -> bool:
        """
        Actualiza el efecto de área.
        Returns: True si sigue activo, False si debe desactivarse
        """
        if not self.state.active:
            return False
        
        # Actualizar tiempo de vida
        self.state.lifetime += dt
        duracion = self.state.spell_data.efecto_params.get("duracion", 
                                                           self.state.spell_data.duracion)
        if self.state.lifetime > duracion:
            return False
        
        # Actualizar timer de tick (para efectos DOT)
        if self._has_tick_damage():
            self.state.tick_timer += dt
        
        return True
    
    def _has_tick_damage(self) -> bool:
        """Verifica si este efecto hace daño por tick"""
        return self.state.spell_data.efecto in [EffectType.DOT, EffectType.HEALING]
    
    def can_affect_enemy(self, enemy_id: int) -> bool:
        """
        Verifica si puede afectar a un enemigo.
        Algunos efectos solo afectan una vez, otros continuamente.
        """
        effect_type = self.state.spell_data.efecto
        
        # Efectos que afectan continuamente (DOT, SLOW, etc.)
        continuous_effects = [
            EffectType.DOT,
            EffectType.SLOW,
            EffectType.CONFUSION
        ]
        
        if effect_type in continuous_effects:
            # Verificar si es tiempo de hacer tick
            if not self._has_tick_damage():
                return True
            
            tick_rate = self.state.spell_data.efecto_params.get("tick_rate", 1.0)
            return self.state.tick_timer >= tick_rate
        
        # Efectos instantáneos (STUN, FREEZE) - solo afectan una vez
        return enemy_id not in self.state.affected_enemies
    
    def on_affect_enemy(self, enemy_id: int):
        """Registra que un enemigo fue afectado"""
        self.state.affected_enemies.add(enemy_id)
        
        # Resetear timer de tick si aplica
        if self._has_tick_damage():
            tick_rate = self.state.spell_data.efecto_params.get("tick_rate", 1.0)
            if self.state.tick_timer >= tick_rate:
                self.state.tick_timer = 0.0
    
    def get_damage(self) -> int:
        """Obtiene el daño que hace este efecto"""
        if self.state.spell_data.efecto == EffectType.DOT:
            return self.state.spell_data.efecto_params.get("tick_damage", 
                                                           self.state.spell_data.daño)
        elif self.state.spell_data.efecto == EffectType.HEALING:
            # Retorna negativo para indicar curación
            return -self.state.spell_data.efecto_params.get("heal_tick", 3)
        
        return self.state.spell_data.daño
    
    def get_radius(self) -> float:
        """Obtiene el radio del efecto"""
        return self.state.spell_data.efecto_params.get("radio", 50)
    
    def deactivate(self):
        """Desactiva el efecto para reutilizarlo"""
        self.state.active = False
        self.state.spell_data = None
        self.state.affected_enemies.clear()
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el efecto de área en pantalla"""
        if not self.state.active:
            return
        
        radius = self.get_radius()
        
        # Calcular alpha para efecto de parpadeo/fade
        alpha = self._calculate_alpha()
        
        # Crear superficie temporal con transparencia
        surf = pygame.Surface((int(radius * 2), int(radius * 2)), pygame.SRCALPHA)
        
        # Dibujar círculo con color primario
        color_with_alpha = (*self.state.spell_data.color_primario, alpha)
        pygame.draw.circle(surf, color_with_alpha, 
                          (int(radius), int(radius)), int(radius))
        
        # Si tiene color secundario, dibujar círculo interno
        if self.state.spell_data.color_secundario:
            inner_radius = max(1, int(radius * 0.6))
            inner_alpha = min(255, int(alpha * 1.3))
            inner_color = (*self.state.spell_data.color_secundario, inner_alpha)
            pygame.draw.circle(surf, inner_color, 
                             (int(radius), int(radius)), inner_radius)
        
        # Blit en posición correcta
        screen.blit(surf, (int(self.state.x - radius), int(self.state.y - radius)))
        
        # DEBUG: Dibujar borde del área de efecto
        # pygame.draw.circle(screen, (255, 255, 0), 
        #                   (int(self.state.x), int(self.state.y)), int(radius), 2)
    
    def _calculate_alpha(self) -> int:
        """Calcula el alpha para efecto visual"""
        duracion = self.state.spell_data.efecto_params.get("duracion", 
                                                           self.state.spell_data.duracion)
        
        # Fade out en el último 20% de vida
        fade_start = duracion * 0.8
        if self.state.lifetime > fade_start:
            remaining = duracion - self.state.lifetime
            fade_duration = duracion - fade_start
            fade_percent = remaining / fade_duration
            return int(180 * fade_percent)
        
        return 180  # Alpha por defecto (semi-transparente)


class AreaEffectPool:
    """
    Pool de efectos de área para reutilización eficiente.
    """
    
    def __init__(self, pool_size: int = 30):
        """
        Args:
            pool_size: Número de efectos pre-creados
        """
        self.pool: List[AreaEffect] = [AreaEffect() for _ in range(pool_size)]
        self.active_effects: List[AreaEffect] = []
    
    def spawn(self, spell_type: SpellType, center_x: float, 
              center_y: float) -> Optional[AreaEffect]:
        """
        Obtiene un efecto inactivo del pool y lo activa.
        Returns: Efecto activado o None si el pool está lleno
        """
        # Buscar efecto inactivo
        for effect in self.pool:
            if not effect.state.active:
                effect.activate(spell_type, center_x, center_y)
                self.active_effects.append(effect)
                return effect
        
        # Pool lleno
        print(f"WARNING: AreaEffectPool lleno ({len(self.pool)} efectos)")
        return None
    
    def spawn_ground_center(self, spell_type: SpellType) -> Optional[AreaEffect]:
        """
        Spawns un efecto en el centro horizontal al ras del suelo.
        Útil para LAVA, BARRO, VAPOR, etc.
        """
        center_x = AreaEffect.SCREEN_WIDTH // 2
        
        # Obtener datos del hechizo para ajustar Y
        spell_data = get_spell_data(spell_type)
        radius = spell_data.efecto_params.get("radio", 50)
        center_y = AreaEffect.SCREEN_HEIGHT - radius
        
        return self.spawn(spell_type, center_x, center_y)
    
    def update(self, dt: float):
        """Actualiza todos los efectos activos"""
        still_active = []
        for effect in self.active_effects:
            if effect.update(dt):
                still_active.append(effect)
            else:
                effect.deactivate()
        
        self.active_effects = still_active
    
    def draw(self, screen: pygame.Surface):
        """Dibuja todos los efectos activos"""
        for effect in self.active_effects:
            effect.draw(screen)
    
    def get_active_effects(self) -> List[AreaEffect]:
        """Retorna lista de efectos activos (para colisiones)"""
        return self.active_effects
    
    def clear_all(self):
        """Desactiva todos los efectos"""
        for effect in self.active_effects:
            effect.deactivate()
        self.active_effects.clear()
    
    def get_stats(self) -> dict:
        """Retorna estadísticas del pool (para debug)"""
        return {
            "total": len(self.pool),
            "active": len(self.active_effects),
            "available": len(self.pool) - len(self.active_effects)
        }