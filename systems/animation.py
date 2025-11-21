import pygame
from typing import List, Optional


class Animation:
    """
    Maneja una animación de sprites.
    Soporta múltiples frames con velocidad configurable.
    """
    
    def __init__(self, frames: List[pygame.Surface], frame_duration: float = 0.1, loop: bool = True):
        """
        Args:
            frames: Lista de superficies de pygame (los frames de la animación)
            frame_duration: Duración de cada frame en segundos
            loop: Si la animación debe repetirse al terminar
        """
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop
        
        self.current_frame = 0
        self.time_accumulated = 0.0
        self.finished = False
        
    def update(self, dt: float):
        """Actualiza la animación"""
        if self.finished and not self.loop:
            return
        
        self.time_accumulated += dt
        
        # Avanzar frames si pasó suficiente tiempo
        while self.time_accumulated >= self.frame_duration:
            self.time_accumulated -= self.frame_duration
            self.current_frame += 1
            
            # Si llegamos al final
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True
    
    def get_current_frame(self) -> pygame.Surface:
        """Retorna el frame actual"""
        return self.frames[self.current_frame]
    
    def reset(self):
        """Reinicia la animación desde el principio"""
        self.current_frame = 0
        self.time_accumulated = 0.0
        self.finished = False
    
    def is_finished(self) -> bool:
        """Verifica si la animación terminó (solo relevante si loop=False)"""
        return self.finished


class AnimationController:
    """
    Controla múltiples animaciones y permite cambiar entre ellas.
    Ejemplo: idle, walk, attack, etc.
    """
    
    def __init__(self):
        self.animations = {}  # Dict[str, Animation]
        self.current_animation_name = None
        self.current_animation = None
        
    def add_animation(self, name: str, animation: Animation):
        """Agrega una animación al controlador"""
        self.animations[name] = animation
        
        # Si es la primera animación, activarla
        if self.current_animation is None:
            self.play(name)
    
    def play(self, name: str, reset: bool = True):
        """
        Cambia a una animación específica.
        
        Args:
            name: Nombre de la animación
            reset: Si debe reiniciar la animación desde el principio
        """
        if name not in self.animations:
            print(f"WARNING: Animación '{name}' no existe")
            return
        
        # Si ya está reproduciendo esta animación, no hacer nada
        if self.current_animation_name == name and not reset:
            return
        
        self.current_animation_name = name
        self.current_animation = self.animations[name]
        
        if reset:
            self.current_animation.reset()
    
    def update(self, dt: float):
        """Actualiza la animación actual"""
        if self.current_animation:
            self.current_animation.update(dt)
    
    def get_current_frame(self) -> Optional[pygame.Surface]:
        """Retorna el frame actual de la animación activa"""
        if self.current_animation:
            return self.current_animation.get_current_frame()
        return None
    
    def get_current_animation_name(self) -> Optional[str]:
        """Retorna el nombre de la animación actual"""
        return self.current_animation_name


def load_animation_frames(folder_path: str, prefix: str, num_frames: int, 
                          scale: tuple = None) -> List[pygame.Surface]:
    """
    Carga múltiples frames de una carpeta.
    
    Args:
        folder_path: Ruta a la carpeta con los frames
        prefix: Prefijo del nombre de archivo (ej: "idle_")
        num_frames: Número de frames a cargar
        scale: Tupla (ancho, alto) para escalar los sprites, o None
        
    Returns:
        Lista de superficies cargadas
        
    Ejemplo de estructura:
        assets/sprites/player/
            idle_0.png
            idle_1.png
            idle_2.png
            cast_0.png
            cast_1.png
    """
    frames = []
    
    for i in range(num_frames):
        try:
            path = f"{folder_path}/{prefix}{i}.png"
            frame = pygame.image.load(path).convert_alpha()
            
            if scale:
                frame = pygame.transform.scale(frame, scale)
            
            frames.append(frame)
        except (pygame.error, FileNotFoundError) as e:
            print(f"WARNING: No se pudo cargar frame {path}: {e}")
            # Crear frame placeholder si falla
            if scale:
                placeholder = pygame.Surface(scale, pygame.SRCALPHA)
            else:
                placeholder = pygame.Surface((32, 32), pygame.SRCALPHA)
            placeholder.fill((255, 0, 255, 128))  # Magenta semi-transparente
            frames.append(placeholder)
    
    return frames


def create_placeholder_frames(num_frames: int, size: tuple, color: tuple) -> List[pygame.Surface]:
    """
    Crea frames placeholder de un solo color (fallback si no hay sprites).
    
    Args:
        num_frames: Número de frames a crear
        size: (ancho, alto) del frame
        color: Color RGB del placeholder
    """
    frames = []
    for _ in range(num_frames):
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (size[0]//2, size[1]//2), min(size)//2)
        frames.append(surf)
    return frames


# ======================
# EJEMPLO DE USO
# ======================

"""
# En tu PlayingState o clase del jugador:

from systems.animation import AnimationController, load_animation_frames, create_placeholder_frames

class Player:
    def __init__(self):
        self.anim_controller = AnimationController()
        
        # Cargar animaciones
        try:
            # Intentar cargar sprites reales
            idle_frames = load_animation_frames(
                "assets/sprites/player", 
                "idle_", 
                4,  # 4 frames
                scale=(50, 50)
            )
            cast_frames = load_animation_frames(
                "assets/sprites/player", 
                "cast_", 
                3,  # 3 frames
                scale=(50, 50)
            )
        except:
            # Fallback: placeholders
            idle_frames = create_placeholder_frames(4, (50, 50), (100, 200, 255))
            cast_frames = create_placeholder_frames(3, (50, 50), (255, 200, 100))
        
        # Crear animaciones
        from systems.animation import Animation
        idle_anim = Animation(idle_frames, frame_duration=0.2, loop=True)
        cast_anim = Animation(cast_frames, frame_duration=0.1, loop=False)
        
        # Agregar al controlador
        self.anim_controller.add_animation("idle", idle_anim)
        self.anim_controller.add_animation("cast", cast_anim)
    
    def cast_spell(self):
        '''Llamar cuando el jugador lance un hechizo'''
        self.anim_controller.play("cast", reset=True)
    
    def update(self, dt):
        self.anim_controller.update(dt)
        
        # Volver a idle cuando termine la animación de cast
        if self.anim_controller.get_current_animation_name() == "cast":
            if self.anim_controller.current_animation.is_finished():
                self.anim_controller.play("idle")
    
    def draw(self, screen, x, y):
        frame = self.anim_controller.get_current_frame()
        if frame:
            rect = frame.get_rect(center=(x, y))
            screen.blit(frame, rect)
"""