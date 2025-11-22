import random
from typing import List, Dict, Callable, Optional
from dataclasses import dataclass
from enum import Enum, auto

from entities.enemies import EnemyManager, EnemyType


# ======================
# ENUMS Y DATACLASSES
# ======================

class WaveState(Enum):
    """Estados de una oleada"""
    WAITING = auto()      # Esperando para iniciar
    SPAWNING = auto()     # Spawneando enemigos
    FIGHTING = auto()     # Combatiendo (todos spawneados)
    COMPLETED = auto()    # Oleada completada
    TRANSITION = auto()   # Transición entre oleadas


@dataclass
class EnemySpawnConfig:
    """Configuración de spawn de un tipo de enemigo"""
    enemy_type: EnemyType
    count: int           # Cantidad a spawnear
    delay: float = 0.0   # Delay antes de empezar a spawnear este tipo


@dataclass
class WaveConfig:
    """Configuración completa de una oleada"""
    wave_number: int
    enemies: List[EnemySpawnConfig]
    spawn_interval: float = 2.0      # Segundos entre spawns
    max_simultaneous: int = 5        # Máximo de enemigos en pantalla a la vez
    reward_points: int = 100         # Puntos al completar la oleada


# ======================
# BASE DE DATOS DE OLEADAS
# ======================

def create_wave_configs() -> List[WaveConfig]:
    """
    Crea la configuración de las 8 oleadas del juego.
    La dificultad aumenta progresivamente.
    """
    waves = [
        # OLEADA 1: Tutorial - Solo slimes
        WaveConfig(
            wave_number=1,
            enemies=[
                EnemySpawnConfig(EnemyType.SLIME, count=5, delay=0.0),
            ],
            spawn_interval=2.5,
            max_simultaneous=3,
            reward_points=100
        ),
        
        # OLEADA 2: Introducción de esqueletos
        WaveConfig(
            wave_number=2,
            enemies=[
                EnemySpawnConfig(EnemyType.SLIME, count=4, delay=0.0),
                EnemySpawnConfig(EnemyType.ESQUELETO, count=3, delay=2.0),
            ],
            spawn_interval=2.0,
            max_simultaneous=4,
            reward_points=150
        ),
        
        # OLEADA 3: Primer murciélago
        WaveConfig(
            wave_number=3,
            enemies=[
                EnemySpawnConfig(EnemyType.SLIME, count=3, delay=0.0),
                EnemySpawnConfig(EnemyType.MURCIELAGO, count=2, delay=3.0),
                EnemySpawnConfig(EnemyType.ESQUELETO, count=3, delay=6.0),
            ],
            spawn_interval=1.8,
            max_simultaneous=4,
            reward_points=200
        ),
        
        # OLEADA 4: Mix equilibrado
        WaveConfig(
            wave_number=4,
            enemies=[
                EnemySpawnConfig(EnemyType.SLIME, count=5, delay=0.0),
                EnemySpawnConfig(EnemyType.MURCIELAGO, count=3, delay=2.0),
                EnemySpawnConfig(EnemyType.ESQUELETO, count=4, delay=4.0),
            ],
            spawn_interval=1.5,
            max_simultaneous=5,
            reward_points=250
        ),
        
        # OLEADA 5: Más murciélagos (énfasis en ataques aéreos)
        WaveConfig(
            wave_number=5,
            enemies=[
                EnemySpawnConfig(EnemyType.MURCIELAGO, count=6, delay=0.0),
                EnemySpawnConfig(EnemyType.ESQUELETO, count=5, delay=3.0),
            ],
            spawn_interval=1.5,
            max_simultaneous=5,
            reward_points=300
        ),
        
        # OLEADA 6: Horda de esqueletos
        WaveConfig(
            wave_number=6,
            enemies=[
                EnemySpawnConfig(EnemyType.ESQUELETO, count=8, delay=0.0),
                EnemySpawnConfig(EnemyType.SLIME, count=6, delay=4.0),
                EnemySpawnConfig(EnemyType.MURCIELAGO, count=4, delay=8.0),
            ],
            spawn_interval=1.2,
            max_simultaneous=6,
            reward_points=350
        ),
        
        # OLEADA 7: Caos - Todos juntos
        WaveConfig(
            wave_number=7,
            enemies=[
                EnemySpawnConfig(EnemyType.SLIME, count=7, delay=0.0),
                EnemySpawnConfig(EnemyType.ESQUELETO, count=7, delay=1.0),
                EnemySpawnConfig(EnemyType.MURCIELAGO, count=6, delay=2.0),
            ],
            spawn_interval=1.0,
            max_simultaneous=7,
            reward_points=400
        ),
        
        # OLEADA 8: BOSS WAVE - Oleada final épica
        WaveConfig(
            wave_number=8,
            enemies=[
                EnemySpawnConfig(EnemyType.MURCIELAGO, count=8, delay=0.0),
                EnemySpawnConfig(EnemyType.ESQUELETO, count=10, delay=3.0),
                EnemySpawnConfig(EnemyType.SLIME, count=10, delay=6.0),
                EnemySpawnConfig(EnemyType.MURCIELAGO, count=8, delay=9.0),
            ],
            spawn_interval=0.8,
            max_simultaneous=8,
            reward_points=500
        ),
    ]
    
    return waves


# ======================
# WAVE MANAGER
# ======================

class WaveManager:
    """
    Gestiona el sistema de oleadas de enemigos.
    Controla el spawning, progresión y transiciones.
    """
    
    def __init__(self, enemy_manager: EnemyManager):
        """
        Args:
            enemy_manager: Instancia del EnemyManager para spawnear enemigos
        """
        self.enemy_manager = enemy_manager
        self.wave_configs = create_wave_configs()
        
        # Estado actual
        self.current_wave_index = 0
        self.wave_state = WaveState.WAITING
        
        # Timers
        self.spawn_timer = 0.0
        self.transition_timer = 0.0
        self.transition_duration = 3.0  # Segundos entre oleadas
        
        # Tracking de spawns
        self.enemies_to_spawn: List[EnemySpawnConfig] = []
        self.current_spawn_queue: List[EnemyType] = []
        self.enemies_spawned_this_wave = 0
        self.spawn_delays: Dict[EnemyType, float] = {}
        
        # Callbacks (opcional)
        self.on_wave_start: Optional[Callable[[int], None]] = None
        self.on_wave_complete: Optional[Callable[[int, int], None]] = None
        self.on_all_waves_complete: Optional[Callable[[], None]] = None
    
    def start_first_wave(self):
        """Inicia la primera oleada"""
        self.start_wave(0)
    
    def start_wave(self, wave_index: int):
        """Inicia una oleada específica"""
        if wave_index >= len(self.wave_configs):
            print("No hay más oleadas")
            return
        
        self.current_wave_index = wave_index
        self.wave_state = WaveState.SPAWNING
        
        current_config = self.wave_configs[wave_index]
        
        # Preparar cola de spawning
        self.enemies_to_spawn = current_config.enemies.copy()
        self.current_spawn_queue = []
        self.enemies_spawned_this_wave = 0
        
        # Preparar delays
        self.spawn_delays = {}
        for enemy_config in self.enemies_to_spawn:
            self.spawn_delays[enemy_config.enemy_type] = enemy_config.delay
        
        # Crear cola de spawn con todos los enemigos
        for enemy_config in self.enemies_to_spawn:
            for _ in range(enemy_config.count):
                self.current_spawn_queue.append(enemy_config.enemy_type)
        
        # Mezclar para variedad
        random.shuffle(self.current_spawn_queue)
        
        self.spawn_timer = 0.0
        
        # Callback
        if self.on_wave_start:
            self.on_wave_start(current_config.wave_number)
        
        print(f"=== OLEADA {current_config.wave_number} INICIADA ===")
        print(f"Enemigos totales: {len(self.current_spawn_queue)}")
    
    def update(self, dt: float):
        """Actualiza el sistema de oleadas"""
        if self.wave_state == WaveState.WAITING:
            # Esperando comando para iniciar
            return
        
        elif self.wave_state == WaveState.SPAWNING:
            self._update_spawning(dt)
        
        elif self.wave_state == WaveState.FIGHTING:
            self._update_fighting()
        
        elif self.wave_state == WaveState.TRANSITION:
            self._update_transition(dt)
    
    def _update_spawning(self, dt: float):
        """Actualiza el estado de spawning"""
        current_config = self.wave_configs[self.current_wave_index]
        
        # Actualizar delays de tipos específicos
        for enemy_type in list(self.spawn_delays.keys()):
            self.spawn_delays[enemy_type] -= dt
        
        # Actualizar timer de spawn
        self.spawn_timer += dt
        
        # Verificar si es momento de spawnear
        if self.spawn_timer >= current_config.spawn_interval:
            self.spawn_timer = 0.0
            
            # Verificar límite de enemigos simultáneos
            current_enemies = len(self.enemy_manager.get_active_enemies())
            
            if current_enemies < current_config.max_simultaneous:
                # Intentar spawnear siguiente enemigo en la cola
                if self.current_spawn_queue:
                    enemy_type = self.current_spawn_queue[0]
                    
                    # Verificar si pasó el delay para este tipo
                    if self.spawn_delays.get(enemy_type, 0) <= 0:
                        self.current_spawn_queue.pop(0)
                        self.enemy_manager.spawn_enemy(enemy_type)
                        self.enemies_spawned_this_wave += 1
        
        # Verificar si terminamos de spawnear todos
        if not self.current_spawn_queue:
            self.wave_state = WaveState.FIGHTING
            print(f"Todos los enemigos spawneados. ¡A luchar!")
    
    def _update_fighting(self):
        """Verifica si la oleada fue completada"""
        # Verificar si todos los enemigos fueron derrotados
        if len(self.enemy_manager.get_active_enemies()) == 0:
            self._complete_wave()
    
    def _complete_wave(self):
        """Completa la oleada actual"""
        current_config = self.wave_configs[self.current_wave_index]
        
        print(f"=== OLEADA {current_config.wave_number} COMPLETADA ===")
        print(f"Recompensa: {current_config.reward_points} puntos")
        
        # Callback
        if self.on_wave_complete:
            self.on_wave_complete(current_config.wave_number, current_config.reward_points)
        
        # Verificar si hay más oleadas
        if self.current_wave_index < len(self.wave_configs) - 1:
            # Ir a transición
            self.wave_state = WaveState.TRANSITION
            self.transition_timer = self.transition_duration
        else:
            # ¡Todas las oleadas completadas!
            self.wave_state = WaveState.COMPLETED
            if self.on_all_waves_complete:
                self.on_all_waves_complete()
            print("=== ¡TODAS LAS OLEADAS COMPLETADAS! ===")
    
    def _update_transition(self, dt: float):
        """Actualiza el estado de transición"""
        self.transition_timer -= dt
        
        if self.transition_timer <= 0:
            # Iniciar siguiente oleada
            self.current_wave_index += 1
            self.start_wave(self.current_wave_index)
    
    def get_current_wave_number(self) -> int:
        """Retorna el número de oleada actual (1-indexed)"""
        if self.current_wave_index < len(self.wave_configs):
            return self.wave_configs[self.current_wave_index].wave_number
        return len(self.wave_configs)
    
    def get_total_waves(self) -> int:
        """Retorna el número total de oleadas"""
        return len(self.wave_configs)
    
    def get_wave_progress(self) -> dict:
        """Retorna información de progreso de la oleada actual"""
        if self.current_wave_index >= len(self.wave_configs):
            return {
                "wave_number": self.get_total_waves(),
                "state": "completed",
                "enemies_remaining": 0,
                "enemies_total": 0,
                "transition_time": 0.0
            }
        
        current_config = self.wave_configs[self.current_wave_index]
        total_enemies = sum(e.count for e in current_config.enemies)
        remaining = len(self.current_spawn_queue) + len(self.enemy_manager.get_active_enemies())
        
        return {
            "wave_number": current_config.wave_number,
            "state": self.wave_state.name.lower(),
            "enemies_remaining": remaining,
            "enemies_total": total_enemies,
            "transition_time": max(0, self.transition_timer)
        }
    
    def is_wave_active(self) -> bool:
        """Verifica si hay una oleada activa"""
        return self.wave_state in (WaveState.SPAWNING, WaveState.FIGHTING)
    
    def force_next_wave(self):
        """Fuerza el inicio de la siguiente oleada (para debug)"""
        if self.current_wave_index < len(self.wave_configs) - 1:
            self.enemy_manager.clear_all()
            self.current_wave_index += 1
            self.start_wave(self.current_wave_index)


# ======================
# EJEMPLO DE USO
# ======================

"""
# En PlayingState:

from systems.wave_manager import WaveManager

class PlayingState(State):
    def _initialize_game(self):
        # ... código existente ...
        
        self.enemy_manager = EnemyManager()
        self.wave_manager = WaveManager(self.enemy_manager)
        
        # Configurar callbacks (opcional)
        self.wave_manager.on_wave_start = self._on_wave_start
        self.wave_manager.on_wave_complete = self._on_wave_complete
        self.wave_manager.on_all_waves_complete = self._on_victory
        
        # Iniciar primera oleada
        self.wave_manager.start_first_wave()
    
    def _on_wave_start(self, wave_number):
        '''Llamado cuando inicia una oleada'''
        print(f"¡Oleada {wave_number} comienza!")
    
    def _on_wave_complete(self, wave_number, reward_points):
        '''Llamado cuando se completa una oleada'''
        self.puntos += reward_points
        print(f"¡Oleada {wave_number} completada! +{reward_points} puntos")
    
    def _on_victory(self):
        '''Llamado cuando se completan todas las oleadas'''
        print("¡VICTORIA!")
        # Ir a pantalla de victoria
        self.game.change_state("victory")
    
    def update(self, dt):
        # ... código existente ...
        
        # Actualizar sistema de oleadas
        self.wave_manager.update(dt)
        
        # Actualizar enemigos (el wave_manager usa enemy_manager internamente)
        self.enemy_manager.update(dt)
        
        # ... resto del código ...
    
    def _draw_ui(self, pantalla):
        # ... código existente ...
        
        # Mostrar info de oleada
        progress = self.wave_manager.get_wave_progress()
        
        if progress["state"] == "transition":
            # Mostrar cuenta regresiva
            txt = self.game.fuente_grande.render(
                f"Oleada {progress['wave_number'] + 1} en {progress['transition_time']:.1f}s",
                True, (255, 255, 0)
            )
            pantalla.blit(txt, (ancho // 2 - txt.get_width() // 2, 300))
        
        elif progress["state"] in ("spawning", "fighting"):
            # Mostrar enemigos restantes
            txt = self.game.fuente_chica.render(
                f"Enemigos: {progress['enemies_remaining']}/{progress['enemies_total']}",
                True, (255, 255, 255)
            )
            pantalla.blit(txt, (10, 120))
"""