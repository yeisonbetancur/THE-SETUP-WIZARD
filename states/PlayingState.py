from states.State import State
import pygame
from config.enums import Element
from systems.spell_system import SpellSystem
from systems.circle import CircleManager
from systems.spell_creator import SpellCastingSystem
from systems.animation import AnimationController, Animation, load_animation_frames, create_placeholder_frames

class PlayingState(State):
    def __init__(self, game):
        """Inicialización única del estado"""
        super().__init__(game)
        self._initialized = False
        
    def enter(self):
        """Llamado cada vez que se entra al estado (inicio Y resume desde pausa)"""
        
        # Inicializar solo la primera vez
        if not self._initialized:
            print("Iniciando partida")
            self._initialize_game()
            self._initialized = True
        else:
            print("Resumiendo partida")
        
        # Iniciar cámara si los gestos están activos
        if self.game.gestos_activos:
            self.game.gesture_detector.iniciar_camara()
    
    def _initialize_game(self):
        """Inicialización completa del juego (solo se llama una vez)"""
        # Jugador estático en esquina inferior izquierda
        self.player_x = 100
        self.player_y = 650
        self.player_hp = 3
        
        # Cargar animaciones del jugador
        self._load_player_animations()
        
        # Sistemas de hechizos
        self.spell_system = SpellSystem(projectile_pool_size=50, area_pool_size=30)
        self.circle_manager = CircleManager()
        self.spell_casting = SpellCastingSystem(
            self.circle_manager,
            self.spell_system
        )
        
        # Estado del juego
        self.puntos = 0
        self.gesto_anterior = "NINGUNO"
        self.oleada_actual = 1
        
        # Estado de animación
        self.ultimo_elemento_lanzado = None
    
    def _load_player_animations(self):
        """Carga todas las animaciones del jugador"""
        self.player_anim = AnimationController()
        player_size = (50, 50)
        
        try:
            # === ANIMACIÓN IDLE (2 frames, loop) ===
            idle_frames = load_animation_frames(
                "assets/sprites/player",
                "idle_",
                num_frames=2,
                scale=player_size
            )
            idle_anim = Animation(idle_frames, frame_duration=0.5, loop=True)
            self.player_anim.add_animation("idle", idle_anim)
            
            # === ANIMACIONES DE ATAQUE (1 frame cada una, no loop) ===
            elementos = ["fuego", "hielo", "rayo", "tierra", "agua", "neutral"]
            
            for elemento in elementos:
                try:
                    # Cargar el frame único de ataque
                    frame_path = f"assets/sprites/player/{elemento}.png"
                    frame = pygame.image.load(frame_path).convert_alpha()
                    frame = pygame.transform.scale(frame, player_size)
                    
                    # Crear animación con el frame repetido (para sostenerlo)
                    # Lo repetimos para que dure más tiempo
                    attack_frames = [frame] * 3  # Mantener el frame 3 veces
                    attack_anim = Animation(attack_frames, frame_duration=0.1, loop=False)
                    
                    self.player_anim.add_animation(f"cast_{elemento}", attack_anim)
                    
                except Exception as e:
                    print(f"WARNING: No se pudo cargar sprite de ataque {elemento}: {e}")
                    # Crear placeholder para este elemento
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
            # Fallback completo: crear placeholders para todo
            idle_frames = create_placeholder_frames(2, player_size, (100, 200, 255))
            idle_anim = Animation(idle_frames, frame_duration=0.5, loop=True)
            self.player_anim.add_animation("idle", idle_anim)
            
            # Crear animaciones de ataque placeholder
            for elemento in ["fuego", "hielo", "rayo", "tierra", "agua", "neutral"]:
                frames = create_placeholder_frames(3, player_size, (255, 100, 100))
                anim = Animation(frames, frame_duration=0.1, loop=False)
                self.player_anim.add_animation(f"cast_{elemento}", anim)
    
    def _play_cast_animation(self, elemento: Element):
        """Reproduce la animación de lanzar hechizo según el elemento"""
        # Mapeo de Element enum a nombre de animación
        element_to_anim = {
            Element.FUEGO: "cast_fuego",
            Element.HIELO: "cast_hielo",
            Element.RAYO: "cast_rayo",
            Element.TIERRA: "cast_tierra",
            Element.AGUA: "cast_agua",
            Element.NEUTRAL: "cast_neutral"
        }
        
        anim_name = element_to_anim.get(elemento, "cast_neutral")
        self.player_anim.play(anim_name, reset=True)
        self.ultimo_elemento_lanzado = elemento
            
    def exit(self):
        print("Saliendo de partida")
        # Limpiar sistemas
        self.spell_casting.clear_all()
        self.spell_system.clear_all()
        
        # Detener cámara al salir
        self.game.gesture_detector.detener_camara()
        
    def handle_events(self, eventos):
        for e in eventos:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.game.change_state("pausa")
                
                # DEBUG: Teclas temporales para testing
                if e.key == pygame.K_1:  # Crear círculo de Fuego
                    self.spell_casting.create_circle(Element.FUEGO)
                elif e.key == pygame.K_2:  # Crear círculo de Hielo
                    self.spell_casting.create_circle(Element.HIELO)
                elif e.key == pygame.K_3:  # Crear círculo de Rayo
                    self.spell_casting.create_circle(Element.RAYO)
                elif e.key == pygame.K_4:  # Crear círculo de Tierra
                    self.spell_casting.create_circle(Element.TIERRA)
                elif e.key == pygame.K_5:  # Crear círculo de Agua
                    self.spell_casting.create_circle(Element.AGUA)
                elif e.key == pygame.K_SPACE:  # Lanzar hechizo
                    self._lanzar_hechizo()
                    
    def update(self, dt):
        # Actualizar animación del jugador
        self.player_anim.update(dt)
        
        # Volver a idle cuando termine la animación de cast
        current_anim = self.player_anim.get_current_animation_name()
        if current_anim and current_anim.startswith("cast_"):
            if self.player_anim.current_animation.is_finished():
                self.player_anim.play("idle")
        
        # Actualizar sistemas de hechizos
        self.spell_casting.update(dt)
        self.spell_system.update(dt)
        
        # Control por gestos
        if self.game.gestos_activos:
            self._actualizar_gestos(dt)
        
        # TODO: Actualizar enemigos
        # TODO: Verificar colisiones proyectiles-enemigos
        # TODO: Verificar colisiones enemigos-jugador
        
    def _actualizar_gestos(self, dt):
        """Procesa los gestos detectados por la cámara"""
        resultado = self.game.gesture_detector.actualizar(dt)
        if not resultado:
            return
        
        gesto_confirmado = self.game.gesture_detector.gesto_confirmado
        
        # Solo procesar si cambió el gesto (evitar spam)
        if gesto_confirmado == self.gesto_anterior:
            return
        
        # Mapeo de gestos a elementos
        if gesto_confirmado == "PAZ":  # ✌️ Hielo
            self.spell_casting.create_circle(Element.HIELO)
            self.gesto_anterior = gesto_confirmado
            
        elif gesto_confirmado == "ROCK":  # 🤘 Fuego
            self.spell_casting.create_circle(Element.FUEGO)
            self.gesto_anterior = gesto_confirmado
            
        elif gesto_confirmado == "ABIERTA":  # ✋ Rayo
            self.spell_casting.create_circle(Element.RAYO)
            self.gesto_anterior = gesto_confirmado
            
        elif gesto_confirmado == "THUMBS_UP":  # 👍 Tierra
            self.spell_casting.create_circle(Element.TIERRA)
            self.gesto_anterior = gesto_confirmado
            
        elif gesto_confirmado == "SHAKA":  # 🤙 Agua
            self.spell_casting.create_circle(Element.AGUA)
            self.gesto_anterior = gesto_confirmado
            
        elif gesto_confirmado == "PUÑO":  # Lanzar hechizo
            self._lanzar_hechizo()
            self.gesto_anterior = gesto_confirmado
        
        # Resetear gesto_anterior si vuelve a NINGUNO
        if gesto_confirmado == "NINGUNO":
            self.gesto_anterior = "NINGUNO"
    
    def _lanzar_hechizo(self):
        """Intenta lanzar un hechizo"""
        # Obtener el spell_type que se va a lanzar
        spell_info = self.spell_casting.get_next_spell_info()
        
        if spell_info:
            # Determinar el elemento principal para la animación
            elemento_anim = self._get_animation_element(spell_info)
            
            # Reproducir animación de cast
            self._play_cast_animation(elemento_anim)
        
        # Intentar lanzar el hechizo
        success = self.spell_casting.cast_spell(self.player_x, self.player_y)
        
        if success:
            # Feedback visual/sonoro (opcional)
            self.puntos += 10
        else:
            # Cooldown activo
            print("Cooldown activo, espera un momento")
    
    def _get_animation_element(self, spell_info):
        """
        Determina qué animación de elemento usar según el hechizo.
        Para combos, usa el primer elemento.
        """
        from config.enums import SpellType
        
        spell_type = spell_info["spell_type"]
        elements = spell_info.get("elements", [])
        
        # Si es un hechizo básico, usar su elemento correspondiente
        basic_spells = {
            SpellType.FUEGO: Element.FUEGO,
            SpellType.HIELO: Element.HIELO,
            SpellType.RAYO: Element.RAYO,
            SpellType.TIERRA: Element.TIERRA,
            SpellType.AGUA: Element.AGUA,
            SpellType.NEUTRAL: Element.NEUTRAL
        }
        
        if spell_type in basic_spells:
            return basic_spells[spell_type]
        
        # Si es un combo, usar el primer elemento
        if elements:
            return elements[0]
        
        # Fallback
        return Element.NEUTRAL
    
    def draw(self, pantalla):
        pantalla.fill((30, 40, 60))  # Fondo oscuro
        
        # Dibujar efectos de área (atrás)
        self.spell_system.draw(pantalla)
        
        # Dibujar círculos mágicos
        self.spell_casting.draw(pantalla)
        
        # Dibujar jugador con animación
        frame = self.player_anim.get_current_frame()
        if frame:
            rect = frame.get_rect(center=(int(self.player_x), int(self.player_y)))
            pantalla.blit(frame, rect)
        else:
            # Fallback extremo: círculo simple
            pygame.draw.circle(pantalla, (100, 200, 255), 
                              (int(self.player_x), int(self.player_y)), 25)
            pygame.draw.circle(pantalla, (255, 255, 255), 
                              (int(self.player_x), int(self.player_y)), 25, 3)
        
        # Dibujar UI
        self._draw_ui(pantalla)
        
    def _draw_ui(self, pantalla):
        """Dibuja la interfaz de usuario"""
        ancho = pantalla.get_width()
        
        # === UI SUPERIOR ===
        y_offset = 10
        
        # Vidas
        vidas_txt = self.game.fuente_chica.render(f"❤️ x{self.player_hp}", True, (255, 50, 50))
        pantalla.blit(vidas_txt, (10, y_offset))
        
        # Oleada
        oleada_txt = self.game.fuente_chica.render(f"Oleada: {self.oleada_actual}/8", True, (255, 255, 255))
        pantalla.blit(oleada_txt, (10, y_offset + 40))
        
        # Puntos
        puntos_txt = self.game.fuente_chica.render(f"Puntos: {self.puntos}", True, (255, 255, 255))
        pantalla.blit(puntos_txt, (10, y_offset + 80))
        
        # === COOLDOWN BAR ===
        cooldown_info = self.spell_casting.get_cooldown_info()
        self._draw_cooldown_bar(pantalla, cooldown_info, 10, y_offset + 120)
        
        # === INFO DE CÍRCULOS ACTIVOS ===
        circle_info = self.spell_casting.get_circle_info()
        self._draw_circle_info(pantalla, circle_info, ancho - 250, 10)
        
        # === CONTROLES ===
        if self.game.gestos_activos:
            self._draw_gesture_controls(pantalla, ancho - 250, 100)
        else:
            self._draw_keyboard_controls(pantalla, ancho - 250, 100)
        
        # === STATS DE POOLS (DEBUG) ===
        if pygame.key.get_pressed()[pygame.K_F3]:  # Presionar F3 para ver debug
            stats = self.spell_system.get_stats()
            self._draw_debug_stats(pantalla, stats, 10, 400)
    
    def _draw_cooldown_bar(self, pantalla, cooldown_info, x, y):
        """Dibuja la barra de cooldown"""
        bar_width = 200
        bar_height = 20
        
        # Fondo de la barra
        pygame.draw.rect(pantalla, (50, 50, 50), (x, y, bar_width, bar_height))
        
        # Barra de progreso
        if not cooldown_info["can_cast"]:
            progress = cooldown_info["percent"]
            fill_width = int(bar_width * progress)
            color = (100, 200, 100) if progress > 0.8 else (200, 200, 100)
            pygame.draw.rect(pantalla, color, (x, y, fill_width, bar_height))
            
            # Texto de tiempo restante
            remaining = cooldown_info["remaining"]
            txt = self.game.fuente_mini.render(f"{remaining:.1f}s", True, (255, 255, 255))
            pantalla.blit(txt, (x + bar_width // 2 - txt.get_width() // 2, y + 2))
        else:
            # Listo para lanzar
            pygame.draw.rect(pantalla, (100, 255, 100), (x, y, bar_width, bar_height))
            txt = self.game.fuente_mini.render("READY!", True, (0, 0, 0))
            pantalla.blit(txt, (x + bar_width // 2 - txt.get_width() // 2, y + 2))
        
        # Borde
        pygame.draw.rect(pantalla, (255, 255, 255), (x, y, bar_width, bar_height), 2)
        
        # Label
        label = self.game.fuente_mini.render("Cooldown:", True, (200, 200, 200))
        pantalla.blit(label, (x, y - 20))
    
    def _draw_circle_info(self, pantalla, circle_info, x, y):
        """Dibuja información de círculos activos"""
        label = self.game.fuente_chica.render("Círculos Activos:", True, (255, 255, 255))
        pantalla.blit(label, (x, y))
        
        y_offset = y + 35
        
        # Mostrar elementos activos
        elements = circle_info.get("elements", [])
        if not elements:
            txt = self.game.fuente_mini.render("(ninguno)", True, (150, 150, 150))
            pantalla.blit(txt, (x + 10, y_offset))
        else:
            for i, elem_name in enumerate(elements):
                # Color según elemento
                colors = {
                    "FUEGO": (255, 100, 50),
                    "HIELO": (100, 200, 255),
                    "RAYO": (255, 255, 100),
                    "TIERRA": (139, 90, 43),
                    "AGUA": (50, 100, 255)
                }
                color = colors.get(elem_name, (200, 200, 200))
                
                # Dibujar círculo pequeño + nombre
                pygame.draw.circle(pantalla, color, (x + 10, y_offset + 10), 8)
                txt = self.game.fuente_mini.render(f"{i+1}. {elem_name}", True, (255, 255, 255))
                pantalla.blit(txt, (x + 25, y_offset))
                
                y_offset += 25
        
        # Contador
        count_txt = self.game.fuente_mini.render(
            f"({circle_info['active_circles']}/{circle_info['max_circles']})",
            True, (150, 150, 150)
        )
        pantalla.blit(count_txt, (x, y + 15))
    
    def _draw_gesture_controls(self, pantalla, x, y):
        """Dibuja la leyenda de controles por gestos"""
        label = self.game.fuente_chica.render("Controles:", True, (255, 255, 255))
        pantalla.blit(label, (x, y))
        
        y_offset = y + 35
        controles = [
            "✌️  PAZ: Hielo",
            "🤘 ROCK: Fuego",
            "✋ ABIERTA: Rayo",
            "👍 THUMBS_UP: Tierra",
            "🤙 SHAKA: Agua",
            "👊 PUÑO: Lanzar",
            "",
            "ESC: Pausa"
        ]
        
        for linea in controles:
            txt = self.game.fuente_mini.render(linea, True, (200, 200, 200))
            pantalla.blit(txt, (x, y_offset))
            y_offset += 22
    
    def _draw_keyboard_controls(self, pantalla, x, y):
        """Dibuja controles de teclado (para testing)"""
        label = self.game.fuente_chica.render("Controles (DEBUG):", True, (255, 255, 255))
        pantalla.blit(label, (x, y))
        
        y_offset = y + 35
        controles = [
            "1: Fuego",
            "2: Hielo",
            "3: Rayo",
            "4: Tierra",
            "5: Agua",
            "SPACE: Lanzar",
            "",
            "ESC: Pausa",
            "F3: Stats"
        ]
        
        for linea in controles:
            txt = self.game.fuente_mini.render(linea, True, (200, 200, 200))
            pantalla.blit(txt, (x, y_offset))
            y_offset += 22
    
    def _draw_debug_stats(self, pantalla, stats, x, y):
        """Dibuja estadísticas de los pools (debug)"""
        label = self.game.fuente_chica.render("DEBUG - Pool Stats:", True, (255, 255, 0))
        pantalla.blit(label, (x, y))
        
        y_offset = y + 30
        
        # Projectiles
        proj = stats["projectiles"]
        txt1 = self.game.fuente_mini.render(
            f"Proyectiles: {proj['active']}/{proj['total']}", 
            True, (255, 255, 255)
        )
        pantalla.blit(txt1, (x, y_offset))
        
        # Area Effects
        area = stats["area_effects"]
        txt2 = self.game.fuente_mini.render(
            f"Áreas: {area['active']}/{area['total']}", 
            True, (255, 255, 255)
        )
        pantalla.blit(txt2, (x, y_offset + 25))