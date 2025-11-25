"""
Estado de Victoria
Mostrado cuando el jugador completa todas las oleadas
"""
from states.State import State
from ui.menu_classes import Button
import pygame
from systems.audio_manager import MusicTrack, SoundEffect


class VictoryState(State):
    """Pantalla de victoria con estadísticas y opciones"""
    
    def __init__(self, game):
        super().__init__(game)
        self.stats = {}
        
    def enter(self):
        """Inicializa la pantalla de victoria"""
        print("🎉 ¡VICTORIA!")
        
        # Detener cámara si estaba activa
        self.game.gesture_detector.detener_camara()
        
        # Reproducir música de victoria
        self.game.audio.stop_music(fade_out=0.5)
        # TODO: Agregar música de victoria cuando tengas el asset
        # self.game.audio.play_music(MusicTrack.VICTORY, loop=False)
        
        # Reproducir sonido de victoria
        # TODO: Agregar sonido de victoria cuando tengas el asset
        # self.game.audio.play_sound(SoundEffect.VICTORY)
        
        # Cargar fondo
        try:
            self.background = pygame.image.load("assets/backgrounds/victory_bg.jpg").convert()
            self.background = pygame.transform.scale(
                self.background, 
                (self.game.pantalla.get_width(), self.game.pantalla.get_height())
            )
        except Exception as e:
            print(f"WARNING: No se pudo cargar background de victoria: {e}")
            self.background = None
        
        # Crear botones
        cx = self.game.pantalla.get_width() // 2
        button_width = 250
        button_height = 50
        
        self.btn_jugar_de_nuevo = Button(
            cx - button_width // 2, 
            500, 
            button_width, 
            button_height, 
            "JUGAR DE NUEVO", 
            self.game.fuente_chica,
            (50, 150, 50),
            (70, 200, 70)
        )
        
        self.btn_menu = Button(
            cx - button_width // 2, 
            570, 
            button_width, 
            button_height, 
            "MENÚ PRINCIPAL", 
            self.game.fuente_chica
        )
        
        self.botones = [self.btn_jugar_de_nuevo, self.btn_menu]
        
        # Animación de título
        self.title_scale = 0.0
        self.title_target = 1.0
        self.title_speed = 3.0
        
        # Animación de estadísticas
        self.stats_alpha = 0
        self.stats_delay = 0.3
        self.stats_timer = 0
        
        # Partículas de celebración (opcional)
        self.particles = []
        self._create_celebration_particles()
    
    def set_stats(self, stats_dict):
        """
        Establece las estadísticas de la partida
        
        Args:
            stats_dict: {
                'puntos': int,
                'oleadas_completadas': int,
                'enemigos_eliminados': int,
                'tiempo_jugado': float (segundos),
                'precision': float (0.0 - 1.0)
            }
        """
        self.stats = stats_dict
    
    def exit(self):
        """Limpieza al salir del estado"""
        print("Saliendo de Victoria")
    
    def handle_events(self, eventos):
        """Maneja eventos de entrada"""
        for e in eventos:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.game.change_state("menu")
                elif e.key == pygame.K_RETURN or e.key == pygame.K_SPACE:
                    self._restart_game()
            
            # Botones
            if self.btn_jugar_de_nuevo.clicked(e):
                self._restart_game()
            elif self.btn_menu.clicked(e):
                self.game.change_state("menu")
    
    def update(self, dt):
        """Actualiza animaciones"""
        # Actualizar hover de botones
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.botones:
            btn.update(mouse_pos)
        
        # Animación del título (escala)
        if self.title_scale < self.title_target:
            self.title_scale += self.title_speed * dt
            if self.title_scale > self.title_target:
                self.title_scale = self.title_target
        
        # Animación de fade-in de estadísticas
        self.stats_timer += dt
        if self.stats_timer > self.stats_delay:
            if self.stats_alpha < 255:
                self.stats_alpha += 400 * dt
                if self.stats_alpha > 255:
                    self.stats_alpha = 255
        
        # Actualizar partículas
        self._update_particles(dt)
    
    def draw(self, pantalla):
        """Renderiza la pantalla de victoria"""
        # Fondo
        if self.background:
            pantalla.blit(self.background, (0, 0))
        else:
            # Fondo degradado verde oscuro -> verde claro
            for y in range(pantalla.get_height()):
                factor = y / pantalla.get_height()
                color = (
                    int(20 + factor * 30),
                    int(40 + factor * 60),
                    int(20 + factor * 30)
                )
                pygame.draw.line(pantalla, color, (0, y), (pantalla.get_width(), y))
        
        # Overlay oscuro semi-transparente
        overlay = pygame.Surface(pantalla.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        pantalla.blit(overlay, (0, 0))
        
        # Dibujar partículas de celebración
        self._draw_particles(pantalla)
        
        # Título "¡VICTORIA!" con animación de escala
        self._draw_title(pantalla)
        
        # Estadísticas
        if self.stats_alpha > 0:
            self._draw_stats(pantalla)
        
        # Botones
        for btn in self.botones:
            btn.draw(pantalla)
        
        # Hint en la parte inferior
        hint_text = self.game.fuente_mini.render(
            "Presiona ENTER para jugar de nuevo o ESC para volver al menú",
            True,
            (200, 200, 200)
        )
        hint_x = pantalla.get_width() // 2 - hint_text.get_width() // 2
        pantalla.blit(hint_text, (hint_x, pantalla.get_height() - 40))
    
    def _draw_title(self, pantalla):
        """Dibuja el título animado"""
        # Texto principal
        title_text = "¡VICTORIA!"
        title_font = pygame.font.Font(None, int(100 * self.title_scale))
        
        # Sombra
        shadow = title_font.render(title_text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(pantalla.get_width() // 2 + 4, 104))
        pantalla.blit(shadow, shadow_rect)
        
        # Texto principal con color dorado
        title = title_font.render(title_text, True, (255, 215, 0))
        title_rect = title.get_rect(center=(pantalla.get_width() // 2, 100))
        pantalla.blit(title, title_rect)
        
        # Subtítulo
        if self.title_scale >= 1.0:
            subtitle = self.game.fuente_chica.render(
                "Has completado todas las oleadas",
                True,
                (200, 200, 200)
            )
            subtitle_rect = subtitle.get_rect(center=(pantalla.get_width() // 2, 170))
            pantalla.blit(subtitle, subtitle_rect)
    
    def _draw_stats(self, pantalla):
        """Dibuja las estadísticas de la partida"""
        cx = pantalla.get_width() // 2
        start_y = 230
        line_height = 50
        
        # Crear superficie con alpha para fade-in
        stats_surface = pygame.Surface((600, 250), pygame.SRCALPHA)
        
        # Fondo semi-transparente para las stats
        pygame.draw.rect(stats_surface, (0, 0, 0, 150), (0, 0, 600, 250), border_radius=15)
        pygame.draw.rect(stats_surface, (255, 215, 0, 200), (0, 0, 600, 250), 3, border_radius=15)
        
        # Título de estadísticas
        stats_title = self.game.fuente_chica.render("Estadísticas", True, (255, 215, 0))
        stats_surface.blit(stats_title, (300 - stats_title.get_width() // 2, 15))
        
        # Línea separadora
        pygame.draw.line(stats_surface, (255, 215, 0), (50, 50), (550, 50), 2)
        
        # Estadísticas individuales
        stats_to_show = [
            ("Puntos Totales", self.stats.get('puntos', 0), (255, 255, 100)),
            ("Oleadas Completadas", self.stats.get('oleadas_completadas', 0), (100, 255, 100)),
            ("Enemigos Eliminados", self.stats.get('enemigos_eliminados', 0), (255, 100, 100)),
        ]
        
        y_offset = 70
        for label, value, color in stats_to_show:
            # Label
            label_text = self.game.fuente_chica.render(label + ":", True, (200, 200, 200))
            stats_surface.blit(label_text, (50, y_offset))
            
            # Valor
            value_text = self.game.fuente_chica.render(str(value), True, color)
            stats_surface.blit(value_text, (500 - value_text.get_width(), y_offset))
            
            y_offset += 45
        
        # Aplicar alpha y dibujar
        stats_surface.set_alpha(int(self.stats_alpha))
        pantalla.blit(stats_surface, (cx - 300, start_y))
    
    def _create_celebration_particles(self):
        """Crea partículas de celebración (confeti)"""
        import random
        
        screen_width = self.game.pantalla.get_width()
        colors = [
            (255, 215, 0),   # Dorado
            (255, 100, 100), # Rojo
            (100, 255, 100), # Verde
            (100, 100, 255), # Azul
            (255, 255, 100), # Amarillo
        ]
        
        for _ in range(50):
            self.particles.append({
                'x': random.randint(0, screen_width),
                'y': random.randint(-100, 0),
                'vx': random.uniform(-50, 50),
                'vy': random.uniform(100, 300),
                'size': random.randint(4, 8),
                'color': random.choice(colors),
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(-200, 200)
            })
    
    def _update_particles(self, dt):
        """Actualiza las partículas de confeti"""
        screen_height = self.game.pantalla.get_height()
        
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['vy'] += 400 * dt  # Gravedad
            particle['rotation'] += particle['rotation_speed'] * dt
            
            # Remover si sale de la pantalla
            if particle['y'] > screen_height + 50:
                self.particles.remove(particle)
    
    def _draw_particles(self, pantalla):
        """Dibuja las partículas de confeti"""
        for particle in self.particles:
            # Dibujar rectángulo rotado (confeti)
            size = particle['size']
            rect_surface = pygame.Surface((size, size * 2), pygame.SRCALPHA)
            pygame.draw.rect(rect_surface, particle['color'], (0, 0, size, size * 2))
            
            # Rotar
            rotated = pygame.transform.rotate(rect_surface, particle['rotation'])
            rect = rotated.get_rect(center=(int(particle['x']), int(particle['y'])))
            pantalla.blit(rotated, rect)
    
    def _restart_game(self):
        """Reinicia el juego"""
        # Reinicializar el estado de juego
        playing_state = self.game.states["jugando"]
        playing_state._initialized = False
        
        # Cambiar al estado de juego
        self.game.change_state("jugando")