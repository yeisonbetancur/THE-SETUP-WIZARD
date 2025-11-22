import pygame
import random
from enum import Enum, auto
from typing import Optional, List, Dict, Set
from dataclasses import dataclass

from config.enums import Element, TrajectoryType
from systems.animation import AnimationController, Animation, load_animation_frames, create_placeholder_frames


# ======================
# ENUMS Y DATACLASSES
# ======================

class EnemyType(Enum):
    """Tipos de enemigos"""
    SLIME = auto()
    ESQUELETO = auto()
    MURCIELAGO = auto()


@dataclass
class EnemyData:
    """Configuración de un tipo de enemigo"""
    nombre: str
    hp: int
    velocidad: float
    daño_al_jugador: int
    tamaño: int  # Radio para colisión
    color_placeholder: tuple  # Color si no hay sprites
    
    # Debilidades elementales (2x daño)
    debilidades: Set[Element]
    
    # Resistencias elementales (0.5x daño)
    resistencias: Set[Element]
    
    # Restricciones de trayectoria (None = cualquiera)
    solo_vulnerable_a: Optional[TrajectoryType] = None
    
    # Animación
    num_frames: int = 2
    frame_duration: float = 0.3


# ======================
# BASE DE DATOS DE ENEMIGOS
# ======================

ENEMY_DATABASE: Dict[EnemyType, EnemyData] = {
    EnemyType.SLIME: EnemyData(
        nombre="Slime",
        hp=30,
        velocidad=60,
        daño_al_jugador=1,
        tamaño=25,
        color_placeholder=(100, 255, 100),
        debilidades={Element.FUEGO, Element.RAYO},  # Débil a fuego y rayo
        resistencias={Element.AGUA},  # Resistente al agua
        solo_vulnerable_a=None,  # Puede ser golpeado por cualquier trayectoria
        num_frames=2,
        frame_duration=0.4
    ),
    
    EnemyType.ESQUELETO: EnemyData(
        nombre="Esqueleto",
        hp=50,
        velocidad=30,
        daño_al_jugador=1,
        tamaño=30,
        color_placeholder=(220, 220, 220),
        debilidades={Element.TIERRA},  # Débil a tierra (aplastamiento)
        resistencias={Element.HIELO},  # Resistente al hielo (ya está muerto)
        solo_vulnerable_a=None,
        num_frames=3,
        frame_duration=0.3
    ),
    
    EnemyType.MURCIELAGO: EnemyData(
        nombre="Murciélago",
        hp=20,
        velocidad=50,
        daño_al_jugador=1,
        tamaño=20,
        color_placeholder=(80, 50, 100),
        debilidades={Element.HIELO},  # Débil a rayo
        resistencias={Element.TIERRA},  # Resistente a tierra (vuela)
        solo_vulnerable_a=TrajectoryType.AEREA,  # ¡Solo vulnerable a ataques aéreos!
        num_frames=2,
        frame_duration=0.2
    ),
}


# ======================
# CLASE ENEMY
# ======================

class Enemy:
    """
    Enemigo base con animaciones, debilidades y movimiento.
    """
    
    # Constantes de pantalla
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    
    # Spawn desde la derecha
    SPAWN_X = SCREEN_WIDTH + 50
    
    def __init__(self, enemy_type: EnemyType, spawn_y: float):
        """
        Args:
            enemy_type: Tipo de enemigo
            spawn_y: Altura Y donde aparece
        """
        self.enemy_type = enemy_type
        self.data = ENEMY_DATABASE[enemy_type]
        
        # Estado
        self.x = self.SPAWN_X
        self.y = spawn_y
        self.hp = self.data.hp
        self.max_hp = self.data.hp
        self.velocidad = self.data.velocidad
        self.activo = True

        self.confused = False
        self.confusion_timer = 0.0
        self.original_velocidad = self.velocidad
        
        # Efectos de estado
        self.slowed = False
        self.slow_factor = 1.0
        self.slow_timer = 0.0
        
        self.stunned = False
        self.stun_timer = 0.0
        self.frozen = False
        
        # DoT (Damage over Time)
        self.dot_active = False
        self.dot_damage = 0
        self.dot_timer = 0.0
        self.dot_tick_rate = 0.5
        self.dot_next_tick = 0.0
        
        # Colisión
        self.rect = pygame.Rect(
            int(self.x - self.data.tamaño),
            int(self.y - self.data.tamaño),
            self.data.tamaño * 2,
            self.data.tamaño * 2
        )
        
        # Animación
        self.anim_controller = None
        self._load_animation()
    
    def _load_animation(self):
        """Carga la animación del enemigo"""
        try:
            enemy_name = self.enemy_type.name.lower()
            frames = load_animation_frames(
                f"assets/sprites/enemies/{enemy_name}",
                "frame_",
                num_frames=self.data.num_frames,
                scale=(self.data.tamaño * 2, self.data.tamaño * 2)
            )
            
            # Verificar si se cargaron sprites válidos
            test_path = f"assets/sprites/enemies/{enemy_name}/frame_0.png"
            pygame.image.load(test_path).convert_alpha()
            
            # Crear animación
            anim = Animation(
                frames,
                frame_duration=self.data.frame_duration,
                loop=True
            )
            
            self.anim_controller = AnimationController()
            self.anim_controller.add_animation("walk", anim)
            self.anim_controller.play("walk")
            
        except Exception as e:
            # Fallback: sin animación, usar gráficos procedurales
            self.anim_controller = None
    
    def update(self, dt: float):
        """Actualiza el enemigo"""
        if not self.activo:
            return
        
        # Actualizar animación
        if self.anim_controller:
            self.anim_controller.update(dt)
        
        # Actualizar efectos de estado
        self._update_status_effects(dt)
        
        # Movimiento (si no está stunned)
        if not self.stunned:
            velocidad_actual = self.velocidad * self.slow_factor
            self.x -= velocidad_actual * dt
        
        # Actualizar rect de colisión
        self.rect.x = int(self.x - self.data.tamaño)
        self.rect.y = int(self.y - self.data.tamaño)
        
        # Desactivar si sale de la pantalla (izquierda)
        if self.x < -50:
            self.activo = False
    
    def _update_status_effects(self, dt: float):
        """Actualiza efectos de estado (slow, stun, DoT)"""
        # Slow
        if self.slowed:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slowed = False
                self.slow_factor = 1.0
        
        # Stun
        if self.stunned:
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.stunned = False
                self.frozen = False  # ← AGREGAR


        if self.confused:
            self.confusion_timer -= dt
            if self.confusion_timer <= 0:
                self.confused = False
                # Restaurar dirección normal (hacia la izquierda)
                self.velocidad = abs(self.original_velocidad)
    
        
        # DoT
        if self.dot_active:
            self.dot_timer -= dt
            self.dot_next_tick -= dt
            
            # Aplicar tick de daño
            if self.dot_next_tick <= 0:
                self.hp -= self.dot_damage
                self.dot_next_tick = self.dot_tick_rate
                
                if self.hp <= 0:
                    self.die()
            
            # Terminar DoT
            if self.dot_timer <= 0:
                self.dot_active = False
    
    def take_damage(self, daño: int, elemento: Element, trayectoria: TrajectoryType) -> bool:
        """
        Aplica daño al enemigo.
        
        Args:
            daño: Daño base del ataque
            elemento: Elemento del ataque
            trayectoria: Trayectoria del proyectil
            
        Returns:
            True si el enemigo puede recibir daño, False si es inmune
        """
        # Verificar si la trayectoria puede dañar a este enemigo
        if self.data.solo_vulnerable_a is not None:
            if trayectoria != self.data.solo_vulnerable_a:
                # Inmune a esta trayectoria
                return False
        
        # Calcular multiplicador elemental
        multiplicador = 1.0
        
        if elemento in self.data.debilidades:
            multiplicador = 2.0  # Doble daño
        elif elemento in self.data.resistencias:
            multiplicador = 0.5  # Mitad de daño
        
        # Aplicar daño
        daño_final = int(daño * multiplicador)
        self.hp -= daño_final
        
        # Verificar muerte
        if self.hp <= 0:
            self.die()
        
        return True
    
    def apply_slow(self, slow_factor: float, duracion: float):
        """Aplica efecto de ralentización"""
        self.slowed = True
        self.slow_factor = slow_factor
        self.slow_timer = duracion
    
    def apply_stun(self, duracion: float,is_freeze: bool = False):
        """Aplica efecto de aturdimiento"""
        self.stunned = True
        self.stun_timer = duracion
        self.frozen = is_freeze  # ← AGREGAR

    
    def apply_dot(self, damage: int, duracion: float, tick_rate: float):
        """Aplica efecto de daño continuo"""
        self.dot_active = True
        self.dot_damage = damage
        self.dot_timer = duracion
        self.dot_tick_rate = tick_rate
        self.dot_next_tick = tick_rate
    
    def die(self):
        """Mata al enemigo"""
        self.activo = False
        self.hp = 0
    
    def is_touching_player(self, player_x: float, player_y: float, player_radius: float = 25) -> bool:
        """Verifica si está tocando al jugador"""
        dist_sq = (self.x - player_x)**2 + (self.y - player_y)**2
        touch_dist = self.data.tamaño + player_radius
        return dist_sq < touch_dist**2
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el enemigo"""
        if not self.activo:
            return

        if self.anim_controller:
            # Usar animación
            frame = self.anim_controller.get_current_frame()
            if frame:
                # Si está congelado, aplicar tinte azul
                if self.frozen:
                    # Crear una copia del frame con tinte azul
                    frozen_frame = frame.copy()
                    frozen_overlay = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
                    frozen_overlay.fill((100, 200, 255, 100))  # Azul semi-transparente
                    frozen_frame.blit(frozen_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    frame = frozen_frame

                rect = frame.get_rect(center=(int(self.x), int(self.y)))
                screen.blit(frame, rect)
        else:
            # Fallback: gráfico procedural
            color = self.data.color_placeholder

            # Si está congelado, cambiar color a azul claro
            if self.frozen:
                color = (100, 200, 255)

            pygame.draw.circle(
                screen,
                color,
                (int(self.x), int(self.y)),
                self.data.tamaño
            )
            pygame.draw.circle(
                screen,
                (255, 255, 255),
                (int(self.x), int(self.y)),
                self.data.tamaño,
                2
            )

        # Dibujar barra de HP
        self._draw_hp_bar(screen)

        # Indicadores de estado
        self._draw_status_indicators(screen)
    
    def _draw_hp_bar(self, screen: pygame.Surface):
        """Dibuja la barra de vida sobre el enemigo"""
        bar_width = self.data.tamaño * 2
        bar_height = 5
        bar_x = int(self.x - bar_width // 2)
        bar_y = int(self.y - self.data.tamaño - 10)

        # Fondo (rojo)
        pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))

        # HP actual (verde)
        hp_percent = max(0, self.hp / self.max_hp)
        fill_width = int(bar_width * hp_percent)
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, fill_width, bar_height))

        # Borde
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)

    def _draw_status_indicators(self, screen: pygame.Surface):
        """Dibuja iconos de efectos de estado"""
        icon_y = int(self.y - self.data.tamaño - 20)
        icon_x = int(self.x - 10)

        if self.stunned:
            if self.frozen:
                # Icono de hielo (azul)
                pygame.draw.circle(screen, (100, 200, 255), (icon_x, icon_y), 4)
                pygame.draw.circle(screen, (200, 240, 255), (icon_x, icon_y), 2)
            else:
                # Estrellitas de aturdimiento (amarillo)
                pygame.draw.circle(screen, (255, 255, 0), (icon_x, icon_y), 3)
            icon_x += 8

        if self.confused:
        # Icono de confusión (espirales moradas/signos de interrogación)
            pygame.draw.circle(screen, (180, 100, 180), (icon_x, icon_y), 4)
            pygame.draw.circle(screen, (220, 150, 220), (icon_x, icon_y), 2)
            icon_x += 8

        if self.slowed:
            # Icono de hielo/ralentización
            pygame.draw.circle(screen, (100, 200, 255), (icon_x, icon_y), 3)
            icon_x += 8

        if self.dot_active:
            # Icono de fuego/veneno
            pygame.draw.circle(screen, (255, 100, 0), (icon_x, icon_y), 3)

    def apply_knockback(self, fuerza: float, direccion_x: float = -1):
        """
        Aplica un empujón al enemigo.

        Args:
            fuerza: Fuerza del empujón en píxeles
            direccion_x: Dirección del empujón (-1 = izquierda, 1 = derecha)
        """
        # Empujar al enemigo
        self.x += direccion_x * fuerza

        # Asegurar que no salga demasiado de la pantalla
        self.x = max(-50, min(self.x, self.SCREEN_WIDTH + 50))


    def apply_confusion(self, duracion: float):
        """
        Aplica efecto de confusión.
        El enemigo cambia de dirección aleatoriamente.
        """
        self.confused = True
        self.confusion_timer = duracion

        # Cambiar dirección: ahora se mueve hacia la derecha (alejándose del jugador)
        self.velocidad = -abs(self.original_velocidad)  # Negativo = hacia la derecha


# ======================
# ENEMY MANAGER
# ======================

class EnemyManager:
    """
    Gestiona el spawn, actualización y eliminación de enemigos.
    """
    
    GROUND_Y = 650  # Altura del suelo
    AIR_Y = 400     # Altura de enemigos voladores
    
    def __init__(self):
        self.enemies: List[Enemy] = []
        self.spawn_timer = 0.0
        self.spawn_interval = 2.0  # Segundos entre spawns
    
    def spawn_enemy(self, enemy_type: EnemyType):
        """Spawnea un enemigo en la derecha de la pantalla"""
        # Determinar altura según tipo
        if enemy_type == EnemyType.MURCIELAGO:
            spawn_y = self.AIR_Y
        else:
            spawn_y = self.GROUND_Y
        
        enemy = Enemy(enemy_type, spawn_y)
        self.enemies.append(enemy)
        return enemy
    
    def spawn_random_enemy(self):
        """Spawnea un enemigo aleatorio"""
        enemy_type = random.choice(list(EnemyType))
        return self.spawn_enemy(enemy_type)
    
    def update(self, dt: float):
        """Actualiza todos los enemigos"""
        # Actualizar enemigos existentes
        for enemy in self.enemies:
            enemy.update(dt)
        
        # Eliminar enemigos inactivos
        self.enemies = [e for e in self.enemies if e.activo]
    
    def draw(self, screen: pygame.Surface):
        """Dibuja todos los enemigos"""
        for enemy in self.enemies:
            enemy.draw(screen)
    
    def clear_all(self):
        """Elimina todos los enemigos (cuando el jugador recibe daño)"""
        for enemy in self.enemies:
            enemy.die()
        self.enemies.clear()
    
    def check_collision_with_player(self, player_x: float, player_y: float) -> bool:
        """
        Verifica si algún enemigo está tocando al jugador.
        
        Returns:
            True si hay colisión, False si no
        """
        for enemy in self.enemies:
            if enemy.is_touching_player(player_x, player_y):
                return True
        return False
    
    def get_active_enemies(self) -> List[Enemy]:
        """Retorna lista de enemigos activos"""
        return self.enemies
    
    def get_stats(self) -> dict:
        """Retorna estadísticas de enemigos"""
        return {
            "total": len(self.enemies),
            "por_tipo": {
                "slime": sum(1 for e in self.enemies if e.enemy_type == EnemyType.SLIME),
                "esqueleto": sum(1 for e in self.enemies if e.enemy_type == EnemyType.ESQUELETO),
                "murcielago": sum(1 for e in self.enemies if e.enemy_type == EnemyType.MURCIELAGO),
            }
        }
    

    


# ======================
# EJEMPLO DE USO
# ======================

"""
# En PlayingState:

from systems.enemy import EnemyManager, EnemyType

class PlayingState(State):
    def _initialize_game(self):
        # ... código existente ...
        
        self.enemy_manager = EnemyManager()
        
        # Spawnear enemigos iniciales
        self.enemy_manager.spawn_enemy(EnemyType.SLIME)
        self.enemy_manager.spawn_enemy(EnemyType.ESQUELETO)
        self.enemy_manager.spawn_enemy(EnemyType.MURCIELAGO)
    
    def update(self, dt):
        # ... código existente ...
        
        # Actualizar enemigos
        self.enemy_manager.update(dt)
        
        # Verificar colisiones proyectiles-enemigos
        for projectile in self.spell_system.get_active_projectiles():
            for enemy in self.enemy_manager.get_active_enemies():
                if projectile.rect.colliderect(enemy.rect):
                    if projectile.can_hit_enemy():
                        # Obtener elemento y trayectoria del proyectil
                        elemento = self._get_element_from_spell(projectile.state.spell_data)
                        trayectoria = projectile.state.trajectory_type
                        
                        # Intentar hacer daño
                        hit = enemy.take_damage(
                            projectile.state.spell_data.daño,
                            elemento,
                            trayectoria
                        )
                        
                        if hit:
                            # Aplicar efectos secundarios
                            self._apply_spell_effects(enemy, projectile.state.spell_data)
                            
                            # Verificar si proyectil debe destruirse
                            if not projectile.on_hit_enemy():
                                projectile.deactivate()
        
        # Verificar colisión enemigos-jugador
        if self.enemy_manager.check_collision_with_player(self.player_x, self.player_y):
            self._player_take_damage()
    
    def _player_take_damage(self):
        '''Llamado cuando un enemigo toca al jugador'''
        self.player_hp -= 1
        
        # Eliminar todos los enemigos
        self.enemy_manager.clear_all()
        
        if self.player_hp <= 0:
            # Game Over
            self.game.change_state("game_over")
    
    def _apply_spell_effects(self, enemy, spell_data):
        '''Aplica efectos de estado según el hechizo'''
        from config.enums import EffectType
        
        efecto = spell_data.efecto
        params = spell_data.efecto_params
        
        if efecto == EffectType.SLOW:
            enemy.apply_slow(params.get("slow_factor", 0.5), params.get("duracion", 2.0))
        
        elif efecto == EffectType.STUN:
            enemy.apply_stun(params.get("duracion", 1.0))
        
        elif efecto == EffectType.DOT:
            enemy.apply_dot(
                params.get("tick_damage", 2),
                params.get("duracion", 3.0),
                params.get("tick_rate", 0.5)
            )
    
    def draw(self, pantalla):
        # ... código existente ...
        
        # Dibujar enemigos
        self.enemy_manager.draw(pantalla)
"""