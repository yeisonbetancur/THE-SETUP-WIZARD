from typing import Optional, List
import time

from config.enums import Element, SpellType
from config.spell_data import buscar_combo, elemento_a_spell_basico


class SpellCreator:
    """
    Determina qué hechizo lanzar según los círculos elementales activos.
    Gestiona los cooldowns de lanzamiento.
    """
    
    def __init__(self):
        # Cooldowns
        self.cooldown_basico = 0.3  # segundos
        self.cooldown_elemental = 2.0  # segundos
        self.last_cast_time = 0.0
        
        # Estado
        self.current_cooldown = 0.0  # Cooldown actual aplicado
        
    def determine_spell(self, active_elements: List[Element]) -> Optional[SpellType]:
        """
        Determina qué hechizo lanzar según los elementos activos.
        
        Args:
            active_elements: Lista de elementos de los círculos activos (0, 1 o 2)
            
        Returns:
            SpellType del hechizo a lanzar, o None si no se puede lanzar
        """
        num_elements = len(active_elements)
        
        if num_elements == 0:
            # Sin círculos = Hechizo básico neutral
            return SpellType.NEUTRAL
            
        elif num_elements == 1:
            # 1 círculo = Hechizo elemental simple
            return elemento_a_spell_basico(active_elements[0])
            
        elif num_elements == 2:
            # 2 círculos = Buscar combo
            elem1, elem2 = active_elements[0], active_elements[1]
            combo = buscar_combo(elem1, elem2)
            
            if combo:
                return combo
            else:
                # Si no existe combo, usar el primer elemento
                print(f"WARNING: No existe combo para {elem1.name} + {elem2.name}")
                return elemento_a_spell_basico(elem1)
        
        # No debería llegar aquí
        return None
    
    def can_cast(self) -> bool:
        """Verifica si se puede lanzar un hechizo (cooldown terminado)"""
        current_time = time.time()
        return (current_time - self.last_cast_time) >= self.current_cooldown
    
    def get_cooldown_remaining(self) -> float:
        """Retorna el tiempo restante de cooldown en segundos"""
        if self.current_cooldown == 0:
            return 0.0
        
        current_time = time.time()
        elapsed = current_time - self.last_cast_time
        remaining = self.current_cooldown - elapsed
        return max(0.0, remaining)
    
    def get_cooldown_percent(self) -> float:
        """Retorna el porcentaje de cooldown completado (0.0 a 1.0)"""
        if self.current_cooldown == 0:
            return 1.0
        
        remaining = self.get_cooldown_remaining()
        return 1.0 - (remaining / self.current_cooldown)
    
    def cast_spell(self, active_elements: List[Element]) -> Optional[SpellType]:
        """
        Intenta lanzar un hechizo si el cooldown lo permite.
        
        Args:
            active_elements: Lista de elementos de los círculos activos
            
        Returns:
            SpellType del hechizo lanzado, o None si no se puede lanzar
        """
        # Verificar cooldown
        if not self.can_cast():
            return None
        
        # Determinar hechizo
        spell_type = self.determine_spell(active_elements)
        if not spell_type:
            return None
        
        # Aplicar cooldown según tipo de hechizo
        num_elements = len(active_elements)
        if num_elements == 0:
            self.current_cooldown = self.cooldown_basico
        else:
            self.current_cooldown = self.cooldown_elemental
        
        # Registrar tiempo de lanzamiento
        self.last_cast_time = time.time()
        
        return spell_type
    
    def reset_cooldown(self):
        """Resetea el cooldown (útil para testing o power-ups)"""
        self.last_cast_time = 0.0
        self.current_cooldown = 0.0


class SpellCastingSystem:
    """
    Sistema completo de lanzamiento de hechizos.
    Integra CircleManager y SpellCreator para gestionar el flujo completo.
    """
    
    def __init__(self, circle_manager, spell_system):
        """
        Args:
            circle_manager: Instancia de CircleManager
            spell_system: Instancia de SpellSystem
        """
        self.circle_manager = circle_manager
        self.spell_system = spell_system
        self.spell_creator = SpellCreator()
        
    def create_circle(self, elemento: Element) -> bool:
        """
        Crea un círculo elemental.
        Wrapper para el CircleManager.
        """
        return self.circle_manager.create_circle(elemento)
    
    def cast_spell(self, player_x: float, player_y: float) -> bool:
        """
        Intenta lanzar un hechizo desde la posición del jugador.
        
        Args:
            player_x: Posición X del jugador
            player_y: Posición Y del jugador
            
        Returns:
            True si se lanzó exitosamente, False si falló (cooldown o error)
        """
        # Obtener elementos activos
        active_elements = self.circle_manager.get_active_elements()
        
        # Intentar lanzar hechizo (verifica cooldown internamente)
        spell_type = self.spell_creator.cast_spell(active_elements)
        
        if not spell_type:
            # No se pudo lanzar (cooldown activo)
            return False
        
        # Lanzar hechizo a través del SpellSystem
        success = self.spell_system.cast_spell(spell_type, player_x, player_y)
        
        if success:
            # Solo consumir círculos si el hechizo se lanzó exitosamente
            # Y solo si había círculos (hechizos elementales)
            if len(active_elements) > 0:
                self.circle_manager.consume_circles()
        
        return success
    
    def update(self, dt: float):
        """Actualiza círculos (el cooldown se maneja automáticamente con time.time())"""
        self.circle_manager.update(dt)
    
    def draw(self, screen):
        """Dibuja los círculos"""
        self.circle_manager.draw(screen)
    
    def can_cast(self) -> bool:
        """Verifica si se puede lanzar un hechizo"""
        return self.spell_creator.can_cast()
    
    def get_cooldown_info(self) -> dict:
        """Retorna información del cooldown para UI"""
        return {
            "can_cast": self.can_cast(),
            "remaining": self.spell_creator.get_cooldown_remaining(),
            "percent": self.spell_creator.get_cooldown_percent()
        }
    
    def get_circle_info(self) -> dict:
        """Retorna información de círculos para UI"""
        return self.circle_manager.get_stats()
    
    def clear_all(self):
        """Limpia círculos y resetea cooldowns"""
        self.circle_manager.clear_all()
        self.spell_creator.reset_cooldown()

    def get_next_spell_info(self) -> Optional[dict]:
        """
        Retorna información sobre el próximo hechizo que se lanzará.
        Útil para mostrar preview o reproducir animaciones antes de lanzar.
        
        Returns:
            Dict con información del hechizo o None si no se puede lanzar
            {
                "spell_type": SpellType,
                "elements": List[Element],  # Elementos usados
                "num_elements": int
            }
        """
        # Obtener elementos activos
        active_elements = self.circle_manager.get_active_elements()
        
        # Determinar qué hechizo se lanzaría
        spell_type = self.spell_creator.determine_spell(active_elements)
        
        if not spell_type:
            return None
        
        return {
            "spell_type": spell_type,
            "elements": active_elements,
            "num_elements": len(active_elements)
        }


# ======================
# EJEMPLO DE USO COMPLETO
# ======================

"""
# En tu PlayingState:

from systems.spell_system import SpellSystem
from systems.circle import CircleManager
from systems.spell_creator import SpellCastingSystem

class PlayingState:
    def __init__(self):
        # Inicializar sistemas
        self.spell_system = SpellSystem()
        self.circle_manager = CircleManager()
        self.spell_casting = SpellCastingSystem(
            self.circle_manager,
            self.spell_system
        )
        
        # Posición del jugador
        self.player_x = 100
        self.player_y = 600
    
    def on_gesture_detected(self, gesture_type):
        '''Llamado cuando se detecta un gesto de mano'''
        
        # Gestos elementales - Crear círculos
        if gesture_type == "PEACE":  # ✌️
            self.spell_casting.create_circle(Element.HIELO)
            
        elif gesture_type == "ROCK":  # 🤘
            self.spell_casting.create_circle(Element.FUEGO)
            
        elif gesture_type == "OPEN_PALM":  # ✋
            self.spell_casting.create_circle(Element.RAYO)
            
        elif gesture_type == "THUMBS_UP":  # 👍
            self.spell_casting.create_circle(Element.TIERRA)
            
        elif gesture_type == "SHAKA":  # 🤙
            self.spell_casting.create_circle(Element.AGUA)
        
        # Gesto de puño - Lanzar hechizo
        elif gesture_type == "FIST":
            success = self.spell_casting.cast_spell(self.player_x, self.player_y)
            if not success:
                print("No se puede lanzar (cooldown activo)")
    
    def update(self, dt):
        # Actualizar sistemas de hechizos
        self.spell_casting.update(dt)
        self.spell_system.update(dt)
        
        # Colisiones con enemigos
        for projectile in self.spell_system.get_active_projectiles():
            for enemy in self.enemies:
                if projectile.rect.colliderect(enemy.rect):
                    if projectile.can_hit_enemy():
                        # Aplicar daño al enemigo
                        enemy.take_damage(projectile.state.spell_data.daño)
                        
                        # Verificar si proyectil debe destruirse
                        if not projectile.on_hit_enemy():
                            projectile.deactivate()
    
    def draw(self, screen):
        # Dibujar círculos
        self.spell_casting.draw(screen)
        
        # Dibujar hechizos
        self.spell_system.draw(screen)
        
        # Dibujar UI de cooldown
        cooldown_info = self.spell_casting.get_cooldown_info()
        if not cooldown_info["can_cast"]:
            # Mostrar barra de cooldown o timer
            remaining = cooldown_info["remaining"]
            print(f"Cooldown: {remaining:.1f}s")
"""