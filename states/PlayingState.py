from states.State import State
import pygame
from config.enums import Element
from systems.spell_system import SpellSystem
from systems.circle import CircleManager
from systems.spell_creator import SpellCastingSystem
from systems.animation import AnimationController, Animation, load_animation_frames, create_placeholder_frames
from entities.enemies import EnemyManager, EnemyType
from systems.wave_manager import WaveManager
from systems.audio_manager import MusicTrack, SoundEffect
from ui.game_hud import GameHUD
from systems.combat_system import CombatSystem
from systems.player_controller import PlayerController
import time
from parallax import ParallaxLayer  


class PlayingState(State):
    """Estado principal del juego - Completamente refactorizado"""
    
    def __init__(self, game):
        """Inicialización única del estado"""
        super().__init__(game)
        self._initialized = False


        
    def enter(self):
        """Llamado cada vez que se entra al estado (inicio Y resume desde pausa)"""
        
        # Inicializar solo la primera vez
        if not self._initialized:
            self._initialize_game()
            self._initialized = True
            # Reproducir música con fade in
            self.game.audio.play_music(MusicTrack.GAMEPLAY, loop=True, fade_in=1.0)
        else:
            self.game.audio.unpause_music()
    
        # Iniciar cámara si los gestos están activos
        if self.game.gestos_activos:
            self.game.gesture_detector.iniciar_camara()
    
    def _initialize_game(self):
        """Inicialización completa del juego (solo se llama una vez)"""
        # === CONFIGURACIÓN DEL JUGADOR ===
        self.player_x = 200
        self.player_y = 640
        self.player_hp = 3

        # === CONFIGURACIÓN DE LA PRINCESA ===
        self.princess_x = 50
        self.princess_y = 200

        # === CARGAR RECURSOS ===
        self._load_background()
        self._load_player_animations()
        self._load_princess_animation()

        # === SISTEMAS DE HECHIZOS ===
        self.spell_system = SpellSystem(projectile_pool_size=50, area_pool_size=30)
        self.circle_manager = CircleManager()
        self.spell_casting = SpellCastingSystem(
            self.circle_manager,
            self.spell_system
        )
        
        # === SISTEMAS DE ENEMIGOS Y OLEADAS ===
        self.enemy_manager = EnemyManager()
        self.wave_manager = WaveManager(self.enemy_manager)

        # Configurar callbacks de oleadas
        self.wave_manager.on_wave_start = self._on_wave_start
        self.wave_manager.on_wave_complete = self._on_wave_complete
        self.wave_manager.on_all_waves_complete = self._on_victory

        # === SISTEMAS REFACTORIZADOS ===
        
        # Sistema de UI
        self.hud = GameHUD({
            'chica': self.game.fuente_chica,
            'mini': self.game.fuente_mini
        })
        
        # Sistema de Combate
        self.combat = CombatSystem(
            self.spell_system,
            self.enemy_manager,
            self.game.audio
        )
        
        # Configurar callbacks de combate
        self.combat.on_projectile_hit = self._on_projectile_hit
        self.combat.on_area_hit = self._on_area_hit
        
        # Sistema de Control del Jugador
        self.player_controller = PlayerController(
            self.spell_casting,
            self.player_anim
        )
        
        # Configurar callbacks del controlador
        self.player_controller.on_spell_cast = self._on_spell_cast
        self.player_controller.on_circle_created = self._on_circle_created
        
        # === ESTADO DEL JUEGO ===
        self.puntos = 0
        self.oleada_actual = 1
        self.enemigos_eliminados = 0
        
        # ✨ Timer de juego para estadísticas
        self.tiempo_inicio = time.time()

        # Iniciar primera oleada
        self.wave_manager.start_first_wave()


    
   
    def _load_background(self):
        pantalla = self.game.pantalla

    # Capas de fondo (parallax)
        self.layers = [
         ParallaxLayer("assets/backgrounds/sprite.fondo1.png", 0, pantalla),   # estática
         ParallaxLayer("assets/backgrounds/sprite.fondo2.png", 1, pantalla),   # derecha → izquierda
         ParallaxLayer("assets/backgrounds/sprite.fondo3.png", -1, pantalla),  # izquierda → derecha
         ParallaxLayer("assets/backgrounds/sprite.fondo4.png", 2, pantalla),   # más rápida
         ParallaxLayer("assets/backgrounds/sprite.fondo5.png", -2, pantalla),  # más rápida en reversa
         ParallaxLayer("assets/backgrounds/sprite.fondo6.png", 0, pantalla),   # estática
         ParallaxLayer("assets/backgrounds/sprite.fondo7.png", 0, pantalla),   # estática
         ParallaxLayer("assets/backgrounds/sprite.fondo8.png", 0, pantalla),   # estática
    ]

            
    
    def _load_player_animations(self):
        """Carga todas las animaciones del jugador"""
        self.player_anim = AnimationController()
        player_size = (100, 100)
        
        try:
            # ANIMACIÓN IDLE
            idle_frames = load_animation_frames(
                "assets/sprites/player",
                "idle_",
                num_frames=2,
                scale=player_size
            )
            idle_anim = Animation(idle_frames, frame_duration=0.5, loop=True)
            self.player_anim.add_animation("idle", idle_anim)
            
            # ANIMACIONES DE ATAQUE
            elementos = ["fuego", "hielo", "rayo", "tierra", "agua", "neutral"]
            
            for elemento in elementos:
                try:
                    frame_path = f"assets/sprites/player/{elemento}.png"
                    frame = pygame.image.load(frame_path).convert_alpha()
                    frame = pygame.transform.scale(frame, player_size)
                    
                    attack_frames = [frame] * 3
                    attack_anim = Animation(attack_frames, frame_duration=0.1, loop=False)
                    
                    self.player_anim.add_animation(f"cast_{elemento}", attack_anim)
                    
                except Exception as e:
                    print(f"WARNING: No se pudo cargar sprite de ataque {elemento}: {e}")
                    colors = {
                        "fuego": (255, 100, 50),
                        "hielo": (100, 200, 255),
                        "rayo": (255, 255, 100),
                        "tierra": (139, 90, 43),
                        "agua": (50, 100, 255),
                        "neutral": (200, 200, 200)
                    }
                    color = colors.get(elemento, (200, 200, 200))
                    placeholder_frames = create_placeholder_frames(3, player_size, color)
                    attack_anim = Animation(placeholder_frames, frame_duration=0.1, loop=False)
                    self.player_anim.add_animation(f"cast_{elemento}", attack_anim)
            
            print("✓ Animaciones del jugador cargadas correctamente")
            
        except Exception as e:
            print(f"ERROR: No se pudieron cargar animaciones del jugador: {e}")
            idle_frames = create_placeholder_frames(2, player_size, (100, 200, 255))
            idle_anim = Animation(idle_frames, frame_duration=0.5, loop=True)
            self.player_anim.add_animation("idle", idle_anim)
            
            for elemento in ["fuego", "hielo", "rayo", "tierra", "agua", "neutral"]:
                frames = create_placeholder_frames(3, player_size, (255, 100, 100))
                anim = Animation(frames, frame_duration=0.1, loop=False)
                self.player_anim.add_animation(f"cast_{elemento}", anim)

    def _load_princess_animation(self):
        """Carga animación de la princesa"""
        self.princess_anim = AnimationController()
        princess_size = (100, 100)
        try:
            idle_frames = load_animation_frames(
                "assets/sprites/princess",
                "idle_",
                num_frames=2,
                scale=princess_size
            )
            idle_anim = Animation(idle_frames, frame_duration=3, loop=True)
            self.princess_anim.add_animation("idle", idle_anim)
        except Exception as e:
            print(f"ERROR: No se pudieron cargar animaciones de la princesa: {e}")
            
    def exit(self):
        """Limpieza al salir del estado"""
        print("Saliendo de partida")
        
        # Limpiar sistemas
        self.spell_casting.clear_all()
        self.spell_system.clear_all()
        self.player_controller.clear()
        
        # Detener cámara
        self.game.gesture_detector.detener_camara()
        
    def handle_events(self, eventos):
        """Maneja eventos de entrada"""
        for e in eventos:
            if e.type == pygame.KEYDOWN:
                # Menú de pausa
                if e.key == pygame.K_ESCAPE:
                    self.game.change_state("pausa")
                
                # DEBUG: Spawn de enemigos
                elif e.key == pygame.K_q:
                    self.enemy_manager.spawn_enemy(EnemyType.SLIME)
                elif e.key == pygame.K_w:
                    self.enemy_manager.spawn_enemy(EnemyType.ESQUELETO)
                elif e.key == pygame.K_e:
                    self.enemy_manager.spawn_enemy(EnemyType.MURCIELAGO)
        
        # Manejar input del jugador (teclado)
        if not self.game.gestos_activos:
            self.player_controller.handle_keyboard_input(eventos)
                    
    def update(self, dt):
        """Actualización principal del juego"""
        # Actualizar fondo por capas
        for layer in self.layers:
           layer.update()

        # Actualizar animaciones
        self.princess_anim.update(dt)
        self.player_controller.update(dt)
        
        # Actualizar sistemas de hechizos
        self.spell_casting.update(dt)
        self.spell_system.update(dt)
        
        # Manejar input por gestos
        if self.game.gestos_activos:
            actions = self.player_controller.handle_gesture_input(
                self.game.gesture_detector, 
                dt
            )
            
            # Lanzar hechizo si el gesto lo activó
            if actions['spell_cast']:
                self.player_controller.cast_spell_at_position(
                    self.player_x, 
                    self.player_y
                )

        # Actualizar oleadas y enemigos
        self.wave_manager.update(dt)
        self.enemy_manager.update(dt)

        # ✨ Actualizar sistema de combate (colisiones)
        combat_stats = self.combat.update(dt)
        
        # Actualizar contador de enemigos eliminados
        if combat_stats['enemies_killed'] > 0:
            self.enemigos_eliminados += combat_stats['enemies_killed']
            self.puntos += combat_stats['enemies_killed'] * 50

        # Verificar colisión enemigo-jugador
        if self.enemy_manager.check_collision_with_player(self.player_x, self.player_y):
            self._player_take_damage()

    def _player_take_damage(self):
        """Llamado cuando un enemigo toca al jugador"""
        self.player_hp -= 1

        # Limpiar enemigos
        self.enemy_manager.clear_all()

        # Feedback
        print(f"¡DAÑO RECIBIDO! HP restante: {self.player_hp}/3")

        # ✨ Game Over
        if self.player_hp <= 0:
            self._trigger_game_over()
    
    def draw(self, pantalla):
        """Renderizado principal del juego"""
        # Dibujar fondo por capas
        for layer in self.layers:
         layer.draw()


        # Flash de daño (si existe)
        if hasattr(self, 'damage_flash_timer') and self.damage_flash_timer > 0:
            flash_overlay = pygame.Surface(pantalla.get_size(), pygame.SRCALPHA)
            alpha = int(150 * (self.damage_flash_timer / 0.3))
            flash_overlay.fill((255, 0, 0, alpha))
            pantalla.blit(flash_overlay, (0, 0))
        
        # Efectos de área (atrás)
        self.spell_system.draw(pantalla)
        
        # Círculos mágicos
        self.spell_casting.draw(pantalla)

        # Princesa
        self._draw_princess(pantalla)
        
        # Jugador
        self._draw_player(pantalla)
        
        # Enemigos
        self.enemy_manager.draw(pantalla)

        # UI
        self.hud.draw(pantalla, self)
    
    def _draw_player(self, pantalla):
        """Dibuja al jugador"""
        frame = self.player_anim.get_current_frame()
        if frame:
            rect = frame.get_rect(center=(int(self.player_x), int(self.player_y)))
            pantalla.blit(frame, rect)
        else:
            pygame.draw.circle(pantalla, (100, 200, 255), 
                              (int(self.player_x), int(self.player_y)), 25)
            pygame.draw.circle(pantalla, (255, 255, 255), 
                              (int(self.player_x), int(self.player_y)), 25, 3)
    
    def _draw_princess(self, pantalla):
        """Dibuja a la princesa"""
        frame = self.princess_anim.get_current_frame()
        if frame:
            rect = frame.get_rect(center=(int(self.princess_x), int(self.princess_y)))
            pantalla.blit(frame, rect)
        else:
            pygame.draw.circle(pantalla, (255, 200, 255), 
                              (int(self.princess_x), int(self.princess_y)), 25)
            pygame.draw.circle(pantalla, (255, 255, 255), 
                              (int(self.princess_x), int(self.princess_y)), 25, 3)
    
    # === CALLBACKS ===
    
    def _on_spell_cast(self, spell_type, success):
        """Callback cuando se lanza un hechizo"""
        if success:
            self.puntos += 10
    
    def _on_circle_created(self, element):
        """Callback cuando se crea un círculo"""
        pass
    
    def _on_projectile_hit(self, projectile, enemy):
        """Callback cuando un proyectil impacta"""
        pass
    
    def _on_area_hit(self, area_effect, enemy):
        """Callback cuando un efecto de área afecta a un enemigo"""
        pass

    def _on_wave_start(self, wave_number):
        """Callback cuando inicia una oleada"""
        self.oleada_actual = wave_number
        print(f"🌊 ¡Oleada {wave_number} comienza!")

    def _on_wave_complete(self, wave_number, reward_points):
        """Callback cuando se completa una oleada"""
        self.puntos += reward_points
        print(f"✅ ¡Oleada {wave_number} completada! +{reward_points} puntos")

    def _on_victory(self):
        """✨ Callback cuando se completan todas las oleadas"""
        print("🎉 ¡VICTORIA!")
        
        # Calcular tiempo jugado
        tiempo_jugado = time.time() - self.tiempo_inicio
        
        # Preparar estadísticas
        stats = {
            'puntos': self.puntos,
            'oleadas_completadas': self.wave_manager.get_total_waves(),
            'enemigos_eliminados': self.enemigos_eliminados,
            'tiempo_jugado': tiempo_jugado,
        }
        
        # Pasar estadísticas al estado de victoria
        victory_state = self.game.states["victoria"]
        victory_state.set_stats(stats)
        
        # Cambiar al estado de victoria
        self.game.change_state("victoria")
    
    def _trigger_game_over(self):
        """✨ Activa la pantalla de Game Over"""
        print("💀 GAME OVER")
        
        # Calcular tiempo sobrevivido
        tiempo_sobrevivido = time.time() - self.tiempo_inicio
        
        # Preparar estadísticas
        stats = {
            'puntos': self.puntos,
            'oleada_alcanzada': self.oleada_actual,
            'enemigos_eliminados': self.enemigos_eliminados,
            'tiempo_sobrevivido': tiempo_sobrevivido,
        }
        
        # Pasar estadísticas al estado de game over
        gameover_state = self.game.states["game_over"]
        gameover_state.set_stats(stats)
        
        # Cambiar al estado de game over
        self.game.change_state("game_over")