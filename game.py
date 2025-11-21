import pygame
import cv2
from gesture_detector import GestureDetector
from abc import ABC, abstractmethod

# ---------------------
# SISTEMA DE DETECCIÓN DE GESTOS
# ---------------------

# ---------------------
# CLASE BOTÓN
# ---------------------
class Button:
    def __init__(self, x, y, ancho, alto, texto, fuente, color=(80, 80, 80), color_hover=(120, 120, 120)):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.fuente = fuente
        self.color = color
        self.color_hover = color_hover
        self.hover = False
        
    def draw(self, pantalla):
        color = self.color_hover if self.hover else self.color
        pygame.draw.rect(pantalla, color, self.rect, border_radius=8)
        pygame.draw.rect(pantalla, (255, 255, 255), self.rect, 2, border_radius=8)
        
        texto_render = self.fuente.render(self.texto, True, (255, 255, 255))
        texto_x = self.rect.centerx - texto_render.get_width() // 2
        texto_y = self.rect.centery - texto_render.get_height() // 2
        pantalla.blit(texto_render, (texto_x, texto_y))
        
    def update(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)
        
    def clicked(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            return self.rect.collidepoint(evento.pos)
        return False

class Slider:
    def __init__(self, x, y, ancho, alto, valor=0.5, min_val=0, max_val=1):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.valor = valor
        self.min_val = min_val
        self.max_val = max_val
        self.dragging = False
        
    def draw(self, pantalla):
        pygame.draw.rect(pantalla, (60, 60, 60), self.rect, border_radius=4)
        progreso_ancho = int((self.valor - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        progreso_rect = pygame.Rect(self.rect.x, self.rect.y, progreso_ancho, self.rect.height)
        pygame.draw.rect(pantalla, (100, 180, 100), progreso_rect, border_radius=4)
        pygame.draw.rect(pantalla, (255, 255, 255), self.rect, 2, border_radius=4)
        perilla_x = self.rect.x + progreso_ancho
        pygame.draw.circle(pantalla, (255, 255, 255), (perilla_x, self.rect.centery), 10)
        
    def handle_event(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                self.dragging = True
                self._update_valor(evento.pos[0])
        elif evento.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif evento.type == pygame.MOUSEMOTION and self.dragging:
            self._update_valor(evento.pos[0])
            
    def _update_valor(self, mouse_x):
        rel_x = mouse_x - self.rect.x
        rel_x = max(0, min(rel_x, self.rect.width))
        self.valor = self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)

class Selector:
    def __init__(self, x, y, ancho, alto, opciones, indice, fuente):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.opciones = opciones
        self.indice = indice
        self.fuente = fuente
        self.btn_izq = pygame.Rect(x, y, 40, alto)
        self.btn_der = pygame.Rect(x + ancho - 40, y, 40, alto)
        
    def draw(self, pantalla):
        pygame.draw.rect(pantalla, (60, 60, 60), self.rect, border_radius=8)
        pygame.draw.rect(pantalla, (255, 255, 255), self.rect, 2, border_radius=8)
        pygame.draw.polygon(pantalla, (255, 255, 255), [
            (self.btn_izq.centerx + 5, self.btn_izq.centery - 8),
            (self.btn_izq.centerx + 5, self.btn_izq.centery + 8),
            (self.btn_izq.centerx - 8, self.btn_izq.centery)
        ])
        pygame.draw.polygon(pantalla, (255, 255, 255), [
            (self.btn_der.centerx - 5, self.btn_der.centery - 8),
            (self.btn_der.centerx - 5, self.btn_der.centery + 8),
            (self.btn_der.centerx + 8, self.btn_der.centery)
        ])
        texto = self.fuente.render(self.opciones[self.indice], True, (255, 255, 255))
        pantalla.blit(texto, (self.rect.centerx - texto.get_width()//2, self.rect.centery - texto.get_height()//2))
        
    def handle_event(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.btn_izq.collidepoint(evento.pos):
                self.indice = (self.indice - 1) % len(self.opciones)
                return True
            elif self.btn_der.collidepoint(evento.pos):
                self.indice = (self.indice + 1) % len(self.opciones)
                return True
        return False
        
    def get_valor(self):
        return self.opciones[self.indice]

# ---------------------
# CLASE BASE STATE
# ---------------------
class State(ABC):
    def __init__(self, game):
        self.game = game
        
    @abstractmethod
    def enter(self):
        pass
        
    @abstractmethod
    def exit(self):
        pass
        
    @abstractmethod
    def handle_events(self, eventos):
        pass
        
    @abstractmethod
    def update(self, dt):
        pass
        
    @abstractmethod
    def draw(self, pantalla):
        pass

# ---------------------
# ESTADOS CONCRETOS
# ---------------------
class MenuState(State):
    def enter(self):
        print("Entrando al menú")
        cx = self.game.pantalla.get_width() // 2
        self.btn_jugar = Button(cx - 100, 280, 200, 50, "JUGAR", self.game.fuente_chica)
        self.btn_opciones = Button(cx - 100, 350, 200, 50, "OPCIONES", self.game.fuente_chica)
        self.btn_salir = Button(cx - 100, 420, 200, 50, "SALIR", self.game.fuente_chica, (120, 50, 50), (180, 70, 70))
        self.botones = [self.btn_jugar, self.btn_opciones, self.btn_salir]
        
    def exit(self):
        print("Saliendo del menú")
        
    def handle_events(self, eventos):
        for e in eventos:
            if self.btn_jugar.clicked(e):
                self.game.change_state("jugando")
            elif self.btn_opciones.clicked(e):
                self.game.change_state("opciones")
            elif self.btn_salir.clicked(e):
                self.game.corriendo = False
                
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.botones:
            btn.update(mouse_pos)
            
    def draw(self, pantalla):
        pantalla.fill((30, 30, 30))
        titulo = self.game.fuente_grande.render("MI JUEGO", True, (255, 255, 255))
        pantalla.blit(titulo, (pantalla.get_width()//2 - titulo.get_width()//2, 150))
        for btn in self.botones:
            btn.draw(pantalla)

class OptionsState(State):
    def enter(self):
        print("Entrando a opciones")
        cx = self.game.pantalla.get_width() // 2
        
        self.slider_volumen = Slider(cx - 100, 200, 200, 20, self.game.volumen)
        
        self.resoluciones = ["800x600", "1024x768", "1280x720"]
        res_actual = f"{self.game.pantalla.get_width()}x{self.game.pantalla.get_height()}"
        indice = self.resoluciones.index(res_actual) if res_actual in self.resoluciones else 0
        self.selector_res = Selector(cx - 120, 300, 240, 40, self.resoluciones, indice, self.game.fuente_chica)
        
        # Selector para activar/desactivar gestos
        self.selector_gestos = Selector(cx - 120, 380, 240, 40, ["DESACTIVADO", "ACTIVADO"], 
                                       1 if self.game.gestos_activos else 0, self.game.fuente_chica)
        
        self.btn_volver = Button(cx - 100, 480, 200, 50, "VOLVER", self.game.fuente_chica)
        
    def exit(self):
        print("Saliendo de opciones")
        
    def handle_events(self, eventos):
        for e in eventos:
            self.slider_volumen.handle_event(e)
            if self.selector_res.handle_event(e):
                res = self.selector_res.get_valor().split("x")
                self.game.set_resolution(int(res[0]), int(res[1]))
                self.enter()
            if self.selector_gestos.handle_event(e):
                self.game.gestos_activos = (self.selector_gestos.get_valor() == "ACTIVADO")
            if self.btn_volver.clicked(e):
                self.game.volumen = self.slider_volumen.valor
                self.game.change_state("menu")
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.game.volumen = self.slider_volumen.valor
                self.game.change_state("menu")
                
    def update(self, dt):
        self.btn_volver.update(pygame.mouse.get_pos())
        
    def draw(self, pantalla):
        pantalla.fill((30, 30, 30))
        titulo = self.game.fuente_grande.render("OPCIONES", True, (255, 255, 255))
        pantalla.blit(titulo, (pantalla.get_width()//2 - titulo.get_width()//2, 80))
        
        lbl_vol = self.game.fuente_chica.render(f"Volumen: {int(self.slider_volumen.valor * 100)}%", True, (255, 255, 255))
        lbl_res = self.game.fuente_chica.render("Resolución:", True, (255, 255, 255))
        lbl_gestos = self.game.fuente_chica.render("Control por Gestos:", True, (255, 255, 255))
        
        pantalla.blit(lbl_vol, (pantalla.get_width()//2 - lbl_vol.get_width()//2, 165))
        pantalla.blit(lbl_res, (pantalla.get_width()//2 - lbl_res.get_width()//2, 265))
        pantalla.blit(lbl_gestos, (pantalla.get_width()//2 - lbl_gestos.get_width()//2, 345))
        
        self.slider_volumen.draw(pantalla)
        self.selector_res.draw(pantalla)
        self.selector_gestos.draw(pantalla)
        self.btn_volver.draw(pantalla)

class PlayingState(State):
    def enter(self):
        print("Iniciando partida")
        self.pos = [400, 300]
        self.color = (255, 200, 0)
        self.puntos = 0
        self.gesto_anterior = "NINGUNO"
        
        # Iniciar cámara si los gestos están activos
        if self.game.gestos_activos:
            self.game.gesture_detector.iniciar_camara()
            
    def exit(self):
        print("Saliendo de partida")
        # Detener cámara al salir
        self.game.gesture_detector.detener_camara()
        
    def handle_events(self, eventos):
        for e in eventos:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.game.change_state("pausa")
                    
    def update(self, dt):
        # Control por teclado
        keys = pygame.key.get_pressed()
        vel = 300 * dt
        if keys[pygame.K_w]: self.pos[1] -= vel
        if keys[pygame.K_s]: self.pos[1] += vel
        if keys[pygame.K_a]: self.pos[0] -= vel
        if keys[pygame.K_d]: self.pos[0] += vel
        
        # Control por gestos
        if self.game.gestos_activos:
            resultado = self.game.gesture_detector.actualizar()
            if resultado:
                gesto = self.game.gesture_detector.ultimo_gesto
                pos_norm = self.game.gesture_detector.posicion_mano
                
                # Mover el círculo con la posición de la mano
                if gesto == "ABIERTA":
                    ancho = self.game.pantalla.get_width()
                    alto = self.game.pantalla.get_height()
                    self.pos[0] = -pos_norm[0] * ancho
                    self.pos[1] = pos_norm[1] * alto
                
                # Cambiar color según el gesto
                if gesto != self.gesto_anterior:
                    if gesto == "PAZ":
                        self.color = (0, 255, 0)
                        self.puntos += 1
                    elif gesto == "ROCK":
                        self.color = (255, 0, 255)
                        self.puntos += 1
                    elif gesto == "SHAKA":
                        self.color = (0, 255, 255)
                        self.puntos += 1
                    elif gesto == "PUÑO":
                        self.color = (255, 0, 0)
                    elif gesto == "ABIERTA":
                        self.color = (255, 200, 0)
                        
                    self.gesto_anterior = gesto
                    
    def draw(self, pantalla):
        pantalla.fill((50, 80, 50))
        
        # Dibujar círculo del jugador
        pygame.draw.circle(pantalla, self.color, (int(self.pos[0]), int(self.pos[1])), 20)
        
        # Información en pantalla
        y_offset = 10
        controles = "WASD mover | ESC pausa"
        if self.game.gestos_activos:
            gesto = self.game.gesture_detector.ultimo_gesto
            controles = f"Gesto: {gesto} | ESC pausa"
            
        texto = self.game.fuente_chica.render(controles, True, (255, 255, 255))
        pantalla.blit(texto, (10, y_offset))
        
        # Puntos
        puntos_txt = self.game.fuente_chica.render(f"Puntos: {self.puntos}", True, (255, 255, 255))
        pantalla.blit(puntos_txt, (10, y_offset + 40))
        
        # Leyenda de gestos
        if self.game.gestos_activos:
            leyenda = [
                "ABIERTA: Mover",
                "PAZ: Verde (+1)",
                "ROCK: Magenta (+1)",
                "SHAKA: Cyan (+1)",
                "PUÑO: Rojo"
            ]
            for i, linea in enumerate(leyenda):
                txt = self.game.fuente_mini.render(linea, True, (200, 200, 200))
                pantalla.blit(txt, (pantalla.get_width() - 200, 10 + i * 25))

class PauseState(State):
    def enter(self):
        print("Juego pausado")
        cx = self.game.pantalla.get_width() // 2
        self.btn_continuar = Button(cx - 100, 280, 200, 50, "CONTINUAR", self.game.fuente_chica)
        self.btn_menu = Button(cx - 100, 350, 200, 50, "MENÚ", self.game.fuente_chica, (120, 50, 50), (180, 70, 70))
        self.botones = [self.btn_continuar, self.btn_menu]
        
        # Pausar detección de gestos
        self.game.gesture_detector.detener_camara()
        
    def exit(self):
        print("Reanudando juego")
        # Reanudar gestos si estaban activos
        if self.game.gestos_activos:
            self.game.gesture_detector.iniciar_camara()
            
    def handle_events(self, eventos):
        for e in eventos:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.game.change_state("jugando")
            if self.btn_continuar.clicked(e):
                self.game.change_state("jugando")
            elif self.btn_menu.clicked(e):
                self.game.change_state("menu")
                
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.botones:
            btn.update(mouse_pos)
            
    def draw(self, pantalla):
        overlay = pygame.Surface(pantalla.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        pantalla.blit(overlay, (0, 0))
        
        texto = self.game.fuente_grande.render("PAUSA", True, (255, 255, 255))
        pantalla.blit(texto, (pantalla.get_width()//2 - texto.get_width()//2, 180))
        
        for btn in self.botones:
            btn.draw(pantalla)

# ---------------------
# GAME (CONTEXT)
# ---------------------
class Game:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("State Pattern con Gestos")
        self.clock = pygame.time.Clock()
        self.corriendo = True
        
        self.fuente_grande = pygame.font.Font(None, 74)
        self.fuente_chica = pygame.font.Font(None, 36)
        self.fuente_mini = pygame.font.Font(None, 24)
        
        # Configuraciones
        self.volumen = 0.5
        self.gestos_activos = True
        
        # Sistema de detección de gestos
        self.gesture_detector = GestureDetector()
        
        # Registro de estados
        self.states = {
            "menu": MenuState(self),
            "jugando": PlayingState(self),
            "pausa": PauseState(self),
            "opciones": OptionsState(self),
        }
        self.current_state = None
        self.change_state("menu")
        
    def set_resolution(self, ancho, alto):
        self.pantalla = pygame.display.set_mode((ancho, alto))
        
    def change_state(self, nombre):
        if self.current_state:
            self.current_state.exit()
        self.current_state = self.states[nombre]
        self.current_state.enter()
        
    def run(self):
        while self.corriendo:
            dt = self.clock.tick(60) / 1000
            eventos = pygame.event.get()
            
            for e in eventos:
                if e.type == pygame.QUIT:
                    self.corriendo = False
                    
            self.current_state.handle_events(eventos)
            self.current_state.update(dt)
            self.current_state.draw(self.pantalla)
            
            pygame.display.flip()
            
        # Limpiar recursos
        self.gesture_detector.detener_camara()
        cv2.destroyAllWindows()
        pygame.quit()

if __name__ == "__main__":
    juego = Game()
    juego.run()