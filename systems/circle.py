import pygame
from typing import List, Optional
from dataclasses import dataclass

from config.enums import Element


@dataclass
class CircleState:
    """Estado interno de un círculo mágico"""
    active: bool = False
    elemento: Optional[Element] = None
    x: float = 0.0
    y: float = 0.0
    lifetime: float = 0.0
    max_lifetime: float = 8.0  # Duración por defecto


class CirculoMagico:
    """
    Círculo elemental flotante que modifica hechizos al ser atravesado.
    Máximo 2 círculos pueden estar activos simultáneamente.
    """
    
    # Constantes visuales
    RADIO_BASE = 40
    RADIO_GLOW = 55
    PULSE_SPEED = 3.0  # Velocidad de pulsación
    
    # Colores por elemento
    ELEMENT_COLORS = {
        Element.FUEGO: (255, 100, 50),
        Element.HIELO: (100, 200, 255),
        Element.RAYO: (255, 255, 100),
        Element.TIERRA: (139, 90, 43),
        Element.AGUA: (50, 100, 255)
    }
    
    # Colores secundarios (para el efecto de glow)
    ELEMENT_GLOW = {
        Element.FUEGO: (255, 200, 0),
        Element.HIELO: (200, 240, 255),
        Element.RAYO: (255, 255, 200),
        Element.TIERRA: (100, 70, 30),
        Element.AGUA: (100, 150, 255)
    }
    
    def __init__(self):
        self.state = CircleState()
        self.pulse_time = 0.0  # Para animación de pulsación
        
    def activate(self, elemento: Element, x: float, y: float, lifetime: float = 8.0):
        """Activa el círculo con un elemento específico"""
        self.state.active = True
        self.state.elemento = elemento
        self.state.x = x
        self.state.y = y
        self.state.lifetime = 0.0
        self.state.max_lifetime = lifetime
        self.pulse_time = 0.0
        
    def update(self, dt: float) -> bool:
        """
        Actualiza el círculo.
        Returns: True si sigue activo, False si debe desactivarse
        """
        if not self.state.active:
            return False
        
        # Actualizar tiempo de vida
        self.state.lifetime += dt
        if self.state.lifetime >= self.state.max_lifetime:
            return False
        
        # Actualizar animación de pulsación
        self.pulse_time += dt * self.PULSE_SPEED
        
        return True
    
    def get_remaining_time(self) -> float:
        """Retorna el tiempo restante del círculo"""
        return max(0, self.state.max_lifetime - self.state.lifetime)
    
    def get_time_percent(self) -> float:
        """Retorna el porcentaje de tiempo restante (0.0 a 1.0)"""
        return self.get_remaining_time() / self.state.max_lifetime
    
    def deactivate(self):
        """Desactiva el círculo para reutilizarlo"""
        self.state.active = False
        self.state.elemento = None
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el círculo con efectos visuales"""
        if not self.state.active:
            return
        
        # Calcular pulsación (oscila entre 0.9 y 1.1)
        pulse = 1.0 + 0.1 * pygame.math.Vector2(1, 0).rotate(self.pulse_time * 360).x
        
        # Calcular alpha según tiempo restante (fade out en últimos 2 segundos)
        time_percent = self.get_time_percent()
        if time_percent < 0.25:  # Últimos 25% de vida
            alpha = int(255 * (time_percent / 0.25))
        else:
            alpha = 255
        
        # Colores del elemento
        color_primary = self.ELEMENT_COLORS[self.state.elemento]
        color_glow = self.ELEMENT_GLOW[self.state.elemento]
        
        # Dibujar glow exterior (con pulsación)
        glow_radius = int(self.RADIO_GLOW * pulse)
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        glow_alpha = min(alpha, 100)
        pygame.draw.circle(glow_surf, (*color_glow, glow_alpha), 
                          (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surf, (int(self.state.x - glow_radius), 
                                int(self.state.y - glow_radius)))
        
        # Dibujar círculo principal
        main_surf = pygame.Surface((self.RADIO_BASE * 2, self.RADIO_BASE * 2), pygame.SRCALPHA)
        pygame.draw.circle(main_surf, (*color_primary, alpha), 
                          (self.RADIO_BASE, self.RADIO_BASE), self.RADIO_BASE)
        screen.blit(main_surf, (int(self.state.x - self.RADIO_BASE), 
                                int(self.state.y - self.RADIO_BASE)))
        
        # Dibujar borde
        pygame.draw.circle(screen, (*color_primary, alpha), 
                          (int(self.state.x), int(self.state.y)), 
                          self.RADIO_BASE, 3)
        
        # Dibujar símbolo del elemento en el centro
        self._draw_element_symbol(screen, alpha)
        
        # Dibujar timer (opcional, para debug/feedback)
        # self._draw_timer(screen, alpha)
    
    def _draw_element_symbol(self, screen: pygame.Surface, alpha: int):
        """Dibuja un símbolo representativo del elemento"""
        # Símbolos simples con formas geométricas
        x, y = int(self.state.x), int(self.state.y)
        color = (255, 255, 255, alpha)
        
        if self.state.elemento == Element.FUEGO:
            # Triángulo hacia arriba (llama)
            points = [(x, y - 15), (x - 10, y + 10), (x + 10, y + 10)]
            pygame.draw.polygon(screen, color[:3], points)
            
        elif self.state.elemento == Element.HIELO:
            # Copo de nieve (asterisco)
            for angle in range(0, 360, 60):
                rad = pygame.math.Vector2(12, 0).rotate(angle)
                end = (x + rad.x, y + rad.y)
                pygame.draw.line(screen, color[:3], (x, y), end, 2)
            
        elif self.state.elemento == Element.RAYO:
            # Rayo zigzag
            points = [(x, y - 12), (x - 6, y - 4), (x + 6, y + 4), (x, y + 12)]
            pygame.draw.lines(screen, color[:3], False, points, 3)
            
        elif self.state.elemento == Element.TIERRA:
            # Cuadrado (roca)
            rect = pygame.Rect(x - 10, y - 10, 20, 20)
            pygame.draw.rect(screen, color[:3], rect, 3)
            
        elif self.state.elemento == Element.AGUA:
            # Onda
            points = []
            for i in range(-10, 11, 2):
                wave_y = y + 5 * pygame.math.Vector2(1, 0).rotate(i * 18).y
                points.append((x + i, wave_y))
            if len(points) > 1:
                pygame.draw.lines(screen, color[:3], False, points, 3)
    
    def _draw_timer(self, screen: pygame.Surface, alpha: int):
        """Dibuja el timer restante (para debug)"""
        remaining = int(self.get_remaining_time())
        font = pygame.font.Font(None, 24)
        text = font.render(str(remaining), True, (255, 255, 255))
        text.set_alpha(alpha)
        text_rect = text.get_rect(center=(int(self.state.x), int(self.state.y) + 50))
        screen.blit(text, text_rect)


class CircleManager:
    """
    Gestiona los círculos mágicos activos.
    Máximo 2 círculos simultáneos, se posicionan en secuencia horizontal.
    """
    
    MAX_CIRCLES = 2
    
    # Posiciones fijas para los círculos (frente al jugador)
    CIRCLE_POSITIONS = [
        (300, 500),  # Primer círculo
        (450, 500),  # Segundo círculo
    ]
    
    def __init__(self):
        self.circles: List[CirculoMagico] = []
        self.circle_lifetime = 8.0  # Duración por defecto
        
    def create_circle(self, elemento: Element) -> bool:
        """
        Crea un nuevo círculo elemental.
        Si ya hay 2 círculos activos, el más antiguo se elimina.
        
        Returns: True si se creó exitosamente
        """
        # Si ya hay MAX_CIRCLES, remover el más antiguo
        if len(self.circles) >= self.MAX_CIRCLES:
            self.circles.pop(0)  # Remover el primero (más antiguo)
        
        # Crear nuevo círculo en la siguiente posición disponible
        position_index = len(self.circles)
        if position_index >= len(self.CIRCLE_POSITIONS):
            position_index = len(self.CIRCLE_POSITIONS) - 1
        
        x, y = self.CIRCLE_POSITIONS[position_index]
        
        new_circle = CirculoMagico()
        new_circle.activate(elemento, x, y, self.circle_lifetime)
        self.circles.append(new_circle)
        
        return True
    
    def update(self, dt: float):
        """Actualiza todos los círculos activos"""
        # Actualizar y filtrar círculos que siguen activos
        still_active = []
        for circle in self.circles:
            if circle.update(dt):
                still_active.append(circle)
            else:
                circle.deactivate()
        
        self.circles = still_active
    
    def draw(self, screen: pygame.Surface):
        """Dibuja todos los círculos activos"""
        for circle in self.circles:
            circle.draw(screen)
    
    def get_active_elements(self) -> List[Element]:
        """
        Retorna la lista de elementos activos en orden.
        Usado por SpellCreator para determinar qué hechizo lanzar.
        """
        return [circle.state.elemento for circle in self.circles]
    
    def consume_circles(self):
        """
        Consume todos los círculos activos (al lanzar un hechizo).
        Los círculos desaparecen y deben ser recreados.
        """
        for circle in self.circles:
            circle.deactivate()
        self.circles.clear()
    
    def get_circle_count(self) -> int:
        """Retorna el número de círculos activos"""
        return len(self.circles)
    
    def clear_all(self):
        """Limpia todos los círculos (útil al cambiar de estado)"""
        self.consume_circles()
    
    def get_stats(self) -> dict:
        """Retorna estadísticas para debug"""
        return {
            "active_circles": len(self.circles),
            "max_circles": self.MAX_CIRCLES,
            "elements": [e.name for e in self.get_active_elements()]
        }


# ======================
# EJEMPLO DE USO
# ======================

"""
# En tu PlayingState:

def __init__(self):
    self.circle_manager = CircleManager()

def on_gesture_detected(self, gesture_type):
    if gesture_type == "PEACE":  # ✌️
        self.circle_manager.create_circle(Element.HIELO)
    elif gesture_type == "ROCK":  # 🤘
        self.circle_manager.create_circle(Element.FUEGO)
    # ... etc

def update(self, dt):
    self.circle_manager.update(dt)

def draw(self, screen):
    self.circle_manager.draw(screen)
"""