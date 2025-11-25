"""
Sistema de UI para el estado de juego
Maneja todo el rendering de la interfaz de usuario
"""
import pygame


class GameHUD:
    """Maneja toda la interfaz de usuario durante el juego"""
    
    def __init__(self, fonts):
        """
        Args:
            fonts: Diccionario con las fuentes del juego
                   {'chica': Font, 'mini': Font}
        """
        self.font_small = fonts.get('chica')
        self.font_mini = fonts.get('mini')
        
        # Configuración de posiciones
        self.padding = 10
        self.line_spacing = 25
        
        # Colores comunes
        self.COLOR_WHITE = (255, 255, 255)
        self.COLOR_GRAY = (200, 200, 200)
        self.COLOR_DARK_GRAY = (150, 150, 150)
        self.COLOR_RED = (255, 50, 50)
        self.COLOR_YELLOW = (255, 255, 0)
        self.COLOR_BLACK = (0, 0, 0)
        self.COLOR_GREEN = (100, 255, 100)
        self.COLOR_LIGHT_GREEN = (100, 200, 100)
        self.COLOR_LIGHT_YELLOW = (200, 200, 100)
        
    def draw(self, screen, game_state):
        """
        Dibuja toda la UI del juego
        
        Args:
            screen: Surface de pygame donde dibujar
            game_state: Referencia al PlayingState con toda la info necesaria
        """
        self._draw_player_stats(screen, game_state)
        self._draw_wave_info(screen, game_state)
        self._draw_score(screen, game_state)
        self._draw_cooldown_bar(screen, game_state)
        self._draw_active_circles(screen, game_state)
        self._draw_controls(screen, game_state)
        
        # Debug info (solo si se presiona F3)
        if pygame.key.get_pressed()[pygame.K_F3]:
            self._draw_debug_info(screen, game_state)
    
    def _draw_player_stats(self, screen, game_state):
        """Dibuja las vidas del jugador"""
        x = self.padding
        y = self.padding
        
        # Corazones de vida
        hp_text = self.font_small.render(
            f"❤️ x{game_state.player_hp}", 
            True, 
            self.COLOR_RED
        )
        screen.blit(hp_text, (x, y))
    
    def _draw_wave_info(self, screen, game_state):
        """Dibuja información de la oleada actual"""
        x = self.padding
        y = self.padding + 40
        
        progress = game_state.wave_manager.get_wave_progress()
        total_waves = game_state.wave_manager.get_total_waves()
        
        # Número de oleada
        wave_text = self.font_small.render(
            f"Oleada: {progress['wave_number']}/{total_waves}",
            True,
            self.COLOR_WHITE
        )
        screen.blit(wave_text, (x, y))
        
        # Enemigos restantes (solo durante combate)
        if progress["state"] in ("spawning", "fighting"):
            y += 30
            enemies_text = self.font_mini.render(
                f"Enemigos: {progress['enemies_remaining']}/{progress['enemies_total']}",
                True,
                self.COLOR_GRAY
            )
            screen.blit(enemies_text, (x, y))
    
    def _draw_score(self, screen, game_state):
        """Dibuja los puntos del jugador"""
        x = self.padding
        y = self.padding + 110
        
        score_text = self.font_small.render(
            f"Puntos: {game_state.puntos}",
            True,
            self.COLOR_WHITE
        )
        screen.blit(score_text, (x, y))
    
    def _draw_cooldown_bar(self, screen, game_state):
        """Dibuja la barra de cooldown de hechizos"""
        x = self.padding
        y = self.padding + 150
        
        cooldown_info = game_state.spell_casting.get_cooldown_info()
        
        # Label
        label = self.font_mini.render("Cooldown:", True, self.COLOR_GRAY)
        screen.blit(label, (x, y - 20))
        
        # Dimensiones de la barra
        bar_width = 200
        bar_height = 20
        
        # Fondo de la barra
        pygame.draw.rect(
            screen, 
            (50, 50, 50), 
            (x, y, bar_width, bar_height)
        )
        
        # Barra de progreso o estado "ready"
        if not cooldown_info["can_cast"]:
            # En cooldown - mostrar progreso
            progress = cooldown_info["percent"]
            fill_width = int(bar_width * progress)
            
            # Color según progreso
            color = self.COLOR_LIGHT_GREEN if progress > 0.8 else self.COLOR_LIGHT_YELLOW
            
            pygame.draw.rect(
                screen, 
                color, 
                (x, y, fill_width, bar_height)
            )
            
            # Texto de tiempo restante
            remaining = cooldown_info["remaining"]
            time_text = self.font_mini.render(
                f"{remaining:.1f}s", 
                True, 
                self.COLOR_WHITE
            )
            text_x = x + bar_width // 2 - time_text.get_width() // 2
            screen.blit(time_text, (text_x, y + 2))
        else:
            # Listo para lanzar
            pygame.draw.rect(
                screen, 
                self.COLOR_GREEN, 
                (x, y, bar_width, bar_height)
            )
            ready_text = self.font_mini.render("READY!", True, self.COLOR_BLACK)
            text_x = x + bar_width // 2 - ready_text.get_width() // 2
            screen.blit(ready_text, (text_x, y + 2))
        
        # Borde de la barra
        pygame.draw.rect(
            screen, 
            self.COLOR_WHITE, 
            (x, y, bar_width, bar_height), 
            2
        )
    
    def _draw_active_circles(self, screen, game_state):
        """Dibuja información de círculos mágicos activos"""
        screen_width = screen.get_width()
        x = screen_width - 250
        y = self.padding
        
        circle_info = game_state.spell_casting.get_circle_info()
        
        # Título
        title = self.font_small.render(
            "Círculos Activos:", 
            True, 
            self.COLOR_WHITE
        )
        screen.blit(title, (x, y))
        
        # Contador
        counter_text = self.font_mini.render(
            f"({circle_info['active_circles']}/{circle_info['max_circles']})",
            True,
            self.COLOR_DARK_GRAY
        )
        screen.blit(counter_text, (x, y + 15))
        
        # Lista de elementos
        y_offset = y + 45
        elements = circle_info.get("elements", [])
        
        if not elements:
            # Sin círculos activos
            none_text = self.font_mini.render(
                "(ninguno)", 
                True, 
                self.COLOR_DARK_GRAY
            )
            screen.blit(none_text, (x + 10, y_offset))
        else:
            # Dibujar cada elemento
            for i, elem_name in enumerate(elements):
                color = self._get_element_color(elem_name)
                
                # Círculo indicador
                circle_x = x + 10
                circle_y = y_offset + 10
                pygame.draw.circle(screen, color, (circle_x, circle_y), 8)
                
                # Nombre del elemento
                elem_text = self.font_mini.render(
                    f"{i+1}. {elem_name}", 
                    True, 
                    self.COLOR_WHITE
                )
                screen.blit(elem_text, (x + 25, y_offset))
                
                y_offset += 25
    
    def _draw_controls(self, screen, game_state):
        """Dibuja la leyenda de controles"""
        screen_width = screen.get_width()
        x = screen_width - 250
        y = 180
        
        # Título
        title = self.font_small.render("Controles:", True, self.COLOR_WHITE)
        screen.blit(title, (x, y))
        
        y_offset = y + 35
        
        # Elegir controles según modo
        if game_state.game.gestos_activos:
            controls = self._get_gesture_controls()
        else:
            controls = self._get_keyboard_controls()
        
        # Dibujar cada línea
        for line in controls:
            text = self.font_mini.render(line, True, self.COLOR_GRAY)
            screen.blit(text, (x, y_offset))
            y_offset += 22
    
    def _draw_debug_info(self, screen, game_state):
        """Dibuja información de debug (F3)"""
        x = self.padding
        y = 400
        
        # Título
        title = self.font_small.render(
            "DEBUG - Pool Stats:", 
            True, 
            self.COLOR_YELLOW
        )
        screen.blit(title, (x, y))
        
        y += 30
        
        # Stats de spell system
        stats = game_state.spell_system.get_stats()
        
        # Proyectiles
        proj = stats["projectiles"]
        proj_text = self.font_mini.render(
            f"Proyectiles: {proj['active']}/{proj['total']}",
            True,
            self.COLOR_WHITE
        )
        screen.blit(proj_text, (x, y))
        
        # Efectos de área
        y += 25
        area = stats["area_effects"]
        area_text = self.font_mini.render(
            f"Áreas: {area['active']}/{area['total']}",
            True,
            self.COLOR_WHITE
        )
        screen.blit(area_text, (x, y))
        
        # Enemigos
        y += 25
        enemy_stats = game_state.enemy_manager.get_stats()
        enemy_text = self.font_mini.render(
            f"Enemigos: {enemy_stats['total']}",
            True,
            self.COLOR_WHITE
        )
        screen.blit(enemy_text, (x, y))
    
    # === MÉTODOS AUXILIARES ===
    
    def _get_element_color(self, element_name):
        """Retorna el color asociado a un elemento"""
        colors = {
            "FUEGO": (255, 100, 50),
            "HIELO": (100, 200, 255),
            "RAYO": (255, 255, 100),
            "TIERRA": (139, 90, 43),
            "AGUA": (50, 100, 255),
            "NEUTRAL": (200, 200, 200)
        }
        return colors.get(element_name, (200, 200, 200))
    
    def _get_gesture_controls(self):
        """Retorna lista de controles por gestos"""
        return [
            "✌️  PAZ: Hielo",
            "🤘 ROCK: Fuego",
            "✋ ABIERTA: Rayo",
            "👍 THUMBS_UP: Tierra",
            "🤙 SHAKA: Agua",
            "👊 PUÑO: Lanzar",
            "",
            "ESC: Pausa"
        ]
    
    def _get_keyboard_controls(self):
        """Retorna lista de controles de teclado (debug)"""
        return [
            "1: Fuego",
            "2: Hielo",
            "3: Rayo",
            "4: Tierra",
            "5: Agua",
            "SPACE: Lanzar",
            "",
            "Q/W/E: Enemigos",
            "ESC: Pausa",
            "F3: Stats"
        ]