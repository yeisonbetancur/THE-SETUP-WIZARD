"""
Estado de Game Over
Mostrado cuando el jugador pierde todas sus vidas
"""
from states.State import State
from ui.menu_classes import Button
import pygame
from systems.audio_manager import MusicTrack, SoundEffect


class GameOverState(State):
    """Pantalla de Game Over con estadísticas y opciones"""
    
    def __init__(self, game):
        super().__init__(game)
        self.stats = {}
        
    def enter(self):
        """Inicializa la pantalla de Game Over"""
        print("💀 GAME OVER")
        
        # Detener cámara si estaba activa
        self.game.gesture_detector.detener_camara()
        
        # Reproducir música de derrota
        self.game.audio.stop_music(fade_out=0.5)
        # TODO: Agregar música de game over cuando tengas el asset
        # self.game.audio.play_music(MusicTrack.GAME_OVER, loop=False)
        
        # Reproducir sonido de derrota
        # TODO: Agregar sonido de game over cuando tengas el asset
        # self.game.audio.play_sound(SoundEffect.GAME_OVER)
        
        # Cargar fondo
        try:
            self.background = pygame.image.load("assets/backgrounds/gameover_bg.jpg").convert()
            self.background = pygame.transform.scale(
                self.background, 
                (self.game.pantalla.get_width(), self.game.pantalla.get_height())
            )
        except Exception as e:
            print(f"WARNING: No se pudo cargar background de game over: {e}")
            self.background = None
        
        # Crear botones
        cx = self.game.pantalla.get_width() // 2
        button_width = 250
        button_height = 50
        
        self.btn_reintentar = Button(
            cx - button_width // 2, 
            500, 
            button_width, 
            button_height, 
            "REINTENTAR", 
            self.game.fuente_chica,
            (150, 50, 50),
            (200, 70, 70)
        )
        
        self.btn_menu = Button(
            cx - button_width // 2, 
            570, 
            button_width, 
            button_height, 
            "MENÚ PRINCIPAL", 
            self.game.fuente_chica
        )
        
        self.botones = [self.btn_reintentar, self.btn_menu]
        
        # Animación de título (fade-in + shake)
        self.title_alpha = 0
        self.title_shake = 0
        self.shake_timer = 0
        
        # Animación de estadísticas
        self.stats_alpha = 0
        self.stats_delay = 0.5
        self.stats_timer = 0
        
        # Efecto de vignette (oscurecimiento en los bordes)
        self.vignette_alpha = 0
    
    def set_stats(self, stats_dict):
        """
        Establece las estadísticas de la partida
        
        Args:
            stats_dict: {
                'puntos': int,
                'oleada_alcanzada': int,
                'enemigos_eliminados': int,
                'tiempo_sobrevivido': float (segundos),
                'causa_muerte': str (opcional)
            }
        """
        self.stats = stats_dict
    
    def exit(self):
        """Limpieza al salir del estado"""
        print("Saliendo de Game Over")
    
    def handle_events(self, eventos):
        """Maneja eventos de entrada"""
        for e in eventos:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.game.change_state("menu")
                elif e.key == pygame.K_RETURN or e.key == pygame.K_SPACE:
                    self._restart_game()
            
            # Botones
            if self.btn_reintentar.clicked(e):
                self._restart_game()
            elif self.btn_menu.clicked(e):
                self.game.change_state("menu")
    
    def update(self, dt):
        """Actualiza animaciones"""
        # Actualizar hover de botones
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.botones:
            btn.update(mouse_pos)
        
        # Animación de fade-in del título
        if self.title_alpha < 255:
            self.title_alpha += 200 * dt
            if self.title_alpha > 255:
                self.title_alpha = 255
        
        # Efecto de shake en el título
        self.shake_timer += dt
        if self.shake_timer < 0.5:  # Shake solo los primeros 0.5 segundos
            import math
            self.title_shake = math.sin(self.shake_timer * 40) * 5 * (1 - self.shake_timer / 0.5)
        else:
            self.title_shake = 0
        
        # Animación de vignette
        if self.vignette_alpha < 180:
            self.vignette_alpha += 100 * dt
            if self.vignette_alpha > 180:
                self.vignette_alpha = 180
        
        # Animación de fade-in de estadísticas
        self.stats_timer += dt
        if self.stats_timer > self.stats_delay:
            if self.stats_alpha < 255:
                self.stats_alpha += 300 * dt
                if self.stats_alpha > 255:
                    self.stats_alpha = 255
    
    def draw(self, pantalla):
        """Renderiza la pantalla de Game Over"""
        # Fondo
        if self.background:
            pantalla.blit(self.background, (0, 0))
        else:
            # Fondo degradado rojo oscuro -> negro
            for y in range(pantalla.get_height()):
                factor = y / pantalla.get_height()
                color = (
                    int(60 * (1 - factor)),
                    int(20 * (1 - factor)),
                    int(20 * (1 - factor))
                )
                pygame.draw.line(pantalla, color, (0, y), (pantalla.get_width(), y))
        
        # Efecto vignette (oscurecimiento en los bordes)
        self._draw_vignette(pantalla)
        
        # Título "GAME OVER" con animación
        self._draw_title(pantalla)
        
        # Estadísticas
        if self.stats_alpha > 0:
            self._draw_stats(pantalla)
        
        # Botones
        for btn in self.botones:
            btn.draw(pantalla)
        
        # Hint en la parte inferior
        hint_text = self.game.fuente_mini.render(
            "Presiona ENTER para reintentar o ESC para volver al menú",
            True,
            (150, 150, 150)
        )
        hint_x = pantalla.get_width() // 2 - hint_text.get_width() // 2
        pantalla.blit(hint_text, (hint_x, pantalla.get_height() - 40))
    
    def _draw_vignette(self, pantalla):
        """Dibuja efecto de vignette (oscurecimiento en los bordes)"""
        if self.vignette_alpha > 0:
            vignette = pygame.Surface(pantalla.get_size(), pygame.SRCALPHA)
            
            # Crear efecto radial
            cx = pantalla.get_width() // 2
            cy = pantalla.get_height() // 2
            max_distance = ((cx ** 2) + (cy ** 2)) ** 0.5
            
            for y in range(0, pantalla.get_height(), 4):
                for x in range(0, pantalla.get_width(), 4):
                    dx = x - cx
                    dy = y - cy
                    distance = (dx ** 2 + dy ** 2) ** 0.5
                    
                    # Factor de oscurecimiento según distancia del centro
                    factor = distance / max_distance
                    alpha = int(self.vignette_alpha * factor)
                    
                    pygame.draw.rect(vignette, (0, 0, 0, alpha), (x, y, 4, 4))
            
            pantalla.blit(vignette, (0, 0))
    
    def _draw_title(self, pantalla):
        """Dibuja el título animado"""
        cx = pantalla.get_width() // 2
        
        # Texto principal
        title_text = "GAME OVER"
        title_font = pygame.font.Font(None, 100)
        
        # Crear superficie para aplicar alpha
        title_surface = pygame.Surface((800, 150), pygame.SRCALPHA)
        
        # Sombra con blur simulado (múltiples capas)
        for offset in range(5, 0, -1):
            shadow = title_font.render(title_text, True, (0, 0, 0, 100))
            shadow_rect = shadow.get_rect(center=(400 + offset + self.title_shake, 75 + offset))
            title_surface.blit(shadow, shadow_rect)
        
        # Texto principal con color rojo sangre
        title = title_font.render(title_text, True, (200, 30, 30))
        title_rect = title.get_rect(center=(400 + self.title_shake, 75))
        title_surface.blit(title, title_rect)
        
        # Aplicar alpha
        title_surface.set_alpha(int(self.title_alpha))
        pantalla.blit(title_surface, (cx - 400, 50))
        
        # Subtítulo
        if self.title_alpha >= 255:
            subtitle = self.game.fuente_chica.render(
                "Has sido derrotado",
                True,
                (150, 150, 150)
            )
            subtitle_rect = subtitle.get_rect(center=(cx, 170))
            pantalla.blit(subtitle, subtitle_rect)
    
    def _draw_stats(self, pantalla):
        """Dibuja las estadísticas de la partida"""
        cx = pantalla.get_width() // 2
        start_y = 230
        
        # Crear superficie con alpha para fade-in
        stats_surface = pygame.Surface((600, 250), pygame.SRCALPHA)
        
        # Fondo semi-transparente para las stats
        pygame.draw.rect(stats_surface, (0, 0, 0, 180), (0, 0, 600, 250), border_radius=15)
        pygame.draw.rect(stats_surface, (200, 50, 50, 200), (0, 0, 600, 250), 3, border_radius=15)
        
        # Título de estadísticas
        stats_title = self.game.fuente_chica.render("Estadísticas Finales", True, (200, 50, 50))
        stats_surface.blit(stats_title, (300 - stats_title.get_width() // 2, 15))
        
        # Línea separadora
        pygame.draw.line(stats_surface, (200, 50, 50), (50, 50), (550, 50), 2)
        
        # Estadísticas individuales
        stats_to_show = [
            ("Puntos Obtenidos", self.stats.get('puntos', 0), (255, 255, 100)),
            ("Oleada Alcanzada", self.stats.get('oleada_alcanzada', 1), (255, 150, 50)),
            ("Enemigos Eliminados", self.stats.get('enemigos_eliminados', 0), (255, 100, 100)),
        ]
        
        # Agregar tiempo si está disponible
        if 'tiempo_sobrevivido' in self.stats:
            tiempo = self.stats['tiempo_sobrevivido']
            minutos = int(tiempo // 60)
            segundos = int(tiempo % 60)
            tiempo_str = f"{minutos}:{segundos:02d}"
            stats_to_show.append(("Tiempo Sobrevivido", tiempo_str, (150, 200, 255)))
        
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
    
    def _restart_game(self):
        """Reinicia el juego"""
        # Reinicializar el estado de juego
        playing_state = self.game.states["jugando"]
        playing_state._initialized = False
        
        # Cambiar al estado de juego
        self.game.change_state("jugando")