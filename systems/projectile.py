import pygame
import math
from typing import List, Optional, Tuple
from dataclasses import dataclass

from config.enums import SpellType, TrajectoryType, BehaviorType
from config.spell_data import get_spell_data, SpellData
from systems.animation import AnimationController, Animation, load_animation_frames, create_placeholder_frames


@dataclass
class ProjectileState:
    """Estado interno de un proyectil"""
    active: bool = False
    x: float = 0.0
    y: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    lifetime: float = 0.0
    enemigos_atravesados: int = 0
    spell_data: Optional[SpellData] = None
    trajectory_type: TrajectoryType = TrajectoryType.FRONTAL


class Projectile:
    """
    Proyectil que viaja por la pantalla.
    Soporta 3 tipos de trayectorias, diferentes comportamientos y animaciones de sprites.
    """
    
    # Constantes de pantalla
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    
    # Constantes de trayectorias
    GRAVITY = 800.0  # Gravedad para trayectorias aéreas (píxeles/s²)
    AEREA_ANGLE = 45  # Ángulo inicial para trayectoria aérea (grados)
    BAJA_Y_OFFSET = 50  # Offset desde el suelo para trayectoria baja
    
    # Constantes de animación
    ANIMATION_FRAMES = 3  # Número de frames por animación
    ANIMATION_FRAME_DURATION = 0.1  # Duración de cada frame en segundos
    
    def __init__(self):
        self.state = ProjectileState()
        self.rect = pygame.Rect(0, 0, 20, 20)  # Colisión básica
        self.anim_controller = None  # Se crea al activar el proyectil
        self.use_animation = False  # Flag para saber si tiene animación o fallback
        
    def _load_animation(self, spell_type: SpellType):
        """Carga la animación del proyectil según el tipo de hechizo"""
        try:
            # Intentar cargar frames desde carpeta del hechizo
            spell_name = spell_type.name.lower()
            folder_path = f"assets/sprites/spells/{spell_name}"

            # Verificar que al menos existe el primer frame
            first_frame_path = f"{folder_path}/frame_0.png"

            # Intentar cargar el primer frame como prueba
            test_frame = pygame.image.load(first_frame_path).convert_alpha()

            # Si llegamos aquí, el archivo existe
            frames = load_animation_frames(
                folder_path,
                "frame_",
                num_frames=self.ANIMATION_FRAMES,
                scale=(self.state.spell_data.tamaño * 2, self.state.spell_data.tamaño * 2)
            )

            # Crear animación
            anim = Animation(
                frames, 
                frame_duration=self.ANIMATION_FRAME_DURATION, 
                loop=True
            )

            # Crear controller y agregar animación
            self.anim_controller = AnimationController()
            self.anim_controller.add_animation("idle", anim)
            self.anim_controller.play("idle")

            self.use_animation = True
            print(f"✓ Animación cargada para {spell_name}")

        except (FileNotFoundError, pygame.error) as e:
            # Fallback: usar gráficos procedurales
            print(f"⚠ No se encontraron sprites para {spell_type.name}, usando fallback: {e}")
            self.anim_controller = None
            self.use_animation = False
    
    def activate(self, spell_type: SpellType, start_x: float, start_y: float, 
                 trajectory: TrajectoryType):
        """Activa el proyectil con un hechizo específico"""
        self.state.active = True
        self.state.spell_data = get_spell_data(spell_type)
        self.state.trajectory_type = trajectory
        self.state.x = start_x
        self.state.y = start_y
        self.state.lifetime = 0.0
        self.state.enemigos_atravesados = 0
        
        # Cargar animación
        self._load_animation(spell_type)
        
        # Configurar velocidad según trayectoria
        self._setup_trajectory()
        
        # Actualizar rect de colisión
        self._update_rect()
        
    def _setup_trajectory(self):
        """Configura la velocidad inicial según el tipo de trayectoria"""
        speed = self.state.spell_data.velocidad
        
        if self.state.trajectory_type == TrajectoryType.FRONTAL:
            # Movimiento horizontal recto
            self.state.vx = speed
            self.state.vy = 0
            
        elif self.state.trajectory_type == TrajectoryType.AEREA:
            # Parábola: ángulo 45° inicial
            angle_rad = math.radians(self.AEREA_ANGLE)
            self.state.vx = speed * math.cos(angle_rad)
            self.state.vy = -speed * math.sin(angle_rad)  # Negativo = hacia arriba
            
        elif self.state.trajectory_type == TrajectoryType.BAJA:
            # Horizontal pero cerca del suelo
            self.state.vx = speed
            self.state.vy = 0
            # Ajustar Y para que esté al ras del suelo
            self.state.y = self.SCREEN_HEIGHT - self.BAJA_Y_OFFSET
    
    def update(self, dt: float) -> bool:
        """
        Actualiza el proyectil.
        Returns: True si sigue activo, False si debe desactivarse
        """
        if not self.state.active:
            return False
        
        # Actualizar tiempo de vida
        self.state.lifetime += dt
        if self.state.lifetime > self.state.spell_data.duracion:
            return False
        
        # Actualizar animación si existe
        if self.use_animation and self.anim_controller:
            self.anim_controller.update(dt)
        
        # Aplicar física según trayectoria
        if self.state.trajectory_type == TrajectoryType.AEREA:
            # Aplicar gravedad
            self.state.vy += self.GRAVITY * dt
        
        # Actualizar posición
        self.state.x += self.state.vx * dt
        self.state.y += self.state.vy * dt
        
        # Verificar límites de pantalla
        if self._out_of_bounds():
            return False
        
        # Actualizar rect de colisión
        self._update_rect()
        
        return True
    
    def _out_of_bounds(self) -> bool:
        """Verifica si el proyectil salió de la pantalla"""
        margin = 50  # Margen para permitir que salga un poco
        return (self.state.x < -margin or 
                self.state.x > self.SCREEN_WIDTH + margin or
                self.state.y < -margin or 
                self.state.y > self.SCREEN_HEIGHT + margin)
    
    def _update_rect(self):
        """Actualiza el rectángulo de colisión"""
        size = self.state.spell_data.tamaño * 2
        self.rect.x = int(self.state.x - self.state.spell_data.tamaño)
        self.rect.y = int(self.state.y - self.state.spell_data.tamaño)
        self.rect.width = size
        self.rect.height = size
    
    def can_hit_enemy(self) -> bool:
        """Verifica si este proyectil puede golpear a un enemigo"""
        if self.state.spell_data is None:  # ← AGREGAR ESTA VERIFICACIÓN
            return False

        behavior = self.state.spell_data.comportamiento

        # CADENA temporalmente se comporta como atraviesa
        if behavior == BehaviorType.ATRAVIESA_ENEMIGOS or behavior == BehaviorType.CADENA:
            max_enemigos = self.state.spell_data.efecto_params.get("max_enemigos", 999)
            if behavior == BehaviorType.CADENA:
                max_enemigos = self.state.spell_data.efecto_params.get("max_saltos", 4)
            return self.state.enemigos_atravesados < max_enemigos

        return True
    
    def on_hit_enemy(self) -> bool:
        """
        Llamado cuando golpea a un enemigo.
        Returns: True si el proyectil debe seguir activo, False si debe destruirse
        """
        if self.state.spell_data is None:  # ← AGREGAR
            return False
            
        behavior = self.state.spell_data.comportamiento
        
        if behavior == BehaviorType.ATRAVIESA_ENEMIGOS or behavior == BehaviorType.CADENA:
            self.state.enemigos_atravesados += 1
            max_enemigos = self.state.spell_data.efecto_params.get("max_enemigos", 999)
            if behavior == BehaviorType.CADENA:
                max_enemigos = self.state.spell_data.efecto_params.get("max_saltos", 4)
            return self.state.enemigos_atravesados < max_enemigos
        
        # Por defecto, el proyectil se destruye al impactar
        return False
    
    def deactivate(self):
        """Desactiva el proyectil para reutilizarlo"""
        self.state.active = False
        self.state.spell_data = None
        self.anim_controller = None
        self.use_animation = False
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el proyectil en pantalla"""
        if not self.state.active:
            return
        
        if self.use_animation and self.anim_controller:
            # Usar animación de sprites
            frame = self.anim_controller.get_current_frame()
            if frame:
                rect = frame.get_rect(center=(int(self.state.x), int(self.state.y)))
                screen.blit(frame, rect)
        else:
            # Fallback: gráficos procedurales (círculos de colores)
            self._draw_procedural(screen)
    
    def _draw_procedural(self, screen: pygame.Surface):
        """Dibuja el proyectil usando gráficos procedurales (fallback)"""
        color = self.state.spell_data.color_primario
        radius = self.state.spell_data.tamaño
        
        # Círculo principal
        pygame.draw.circle(
            screen, 
            color, 
            (int(self.state.x), int(self.state.y)), 
            radius
        )
        
        # Círculo interior (si hay color secundario)
        if self.state.spell_data.color_secundario:
            inner_radius = max(1, radius // 2)
            pygame.draw.circle(
                screen, 
                self.state.spell_data.color_secundario, 
                (int(self.state.x), int(self.state.y)), 
                inner_radius
            )
        
        # Brillo central (opcional, para más detalle)
        highlight_radius = max(1, radius // 4)
        highlight_color = tuple(min(255, c + 100) for c in color)
        pygame.draw.circle(
            screen,
            highlight_color,
            (int(self.state.x - radius // 3), int(self.state.y - radius // 3)),
            highlight_radius
        )


class ProjectilePool:
    """
    Pool de proyectiles para reutilización eficiente.
    Evita crear/destruir objetos constantemente.
    """
    
    def __init__(self, pool_size: int = 50):
        """
        Args:
            pool_size: Número de proyectiles pre-creados
        """
        self.pool: List[Projectile] = [Projectile() for _ in range(pool_size)]
        self.active_projectiles: List[Projectile] = []
    
    def spawn(self, spell_type: SpellType, start_x: float, start_y: float,
              trajectory: TrajectoryType) -> Optional[Projectile]:
        """
        Obtiene un proyectil inactivo del pool y lo activa.
        Returns: Proyectil activado o None si el pool está lleno
        """
        # Buscar proyectil inactivo
        for projectile in self.pool:
            if not projectile.state.active:
                projectile.activate(spell_type, start_x, start_y+25, trajectory)
                self.active_projectiles.append(projectile)
                return projectile
        
        # Pool lleno
        print(f"WARNING: ProjectilePool lleno ({len(self.pool)} proyectiles)")
        return None
    
    def update(self, dt: float):
        """Actualiza todos los proyectiles activos"""
        # Actualizar y filtrar proyectiles que siguen activos
        still_active = []
        for projectile in self.active_projectiles:
            if projectile.update(dt):
                still_active.append(projectile)
            else:
                projectile.deactivate()
        
        self.active_projectiles = still_active
    
    def draw(self, screen: pygame.Surface):
        """Dibuja todos los proyectiles activos"""
        for projectile in self.active_projectiles:
            projectile.draw(screen)
    
    def get_active_projectiles(self) -> List[Projectile]:
        """Retorna lista de proyectiles activos (para colisiones)"""
        return self.active_projectiles
    
    def clear_all(self):
        """Desactiva todos los proyectiles (útil al cambiar de oleada)"""
        for projectile in self.active_projectiles:
            projectile.deactivate()
        self.active_projectiles.clear()
    
    def get_stats(self) -> dict:
        """Retorna estadísticas del pool (para debug)"""
        return {
            "total": len(self.pool),
            "active": len(self.active_projectiles),
            "available": len(self.pool) - len(self.active_projectiles)
        }


# ======================
# EJEMPLO DE USO
# ======================

"""
# En PlayingState:

from systems.projectile import ProjectilePool
from config.enums import SpellType, TrajectoryType

class PlayingState(State):
    def enter(self):
        self.projectile_pool = ProjectilePool(pool_size=50)
    
    def lanzar_hechizo(self, spell_type: SpellType, trajectory: TrajectoryType):
        # Lanzar desde posición del jugador
        player_x = 100
        player_y = 300
        
        self.projectile_pool.spawn(spell_type, player_x, player_y, trajectory)
    
    def update(self, dt):
        self.projectile_pool.update(dt)
        
        # Debug: ver cuántos proyectiles hay activos
        stats = self.projectile_pool.get_stats()
        print(f"Proyectiles: {stats['active']}/{stats['total']}")
    
    def draw(self, pantalla):
        pantalla.fill((50, 80, 50))
        self.projectile_pool.draw(pantalla)
"""