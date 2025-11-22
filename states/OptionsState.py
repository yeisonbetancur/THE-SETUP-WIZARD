from ui.menu_classes import Slider, Selector, Button
from states.State import State
import pygame

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
                self.game.audio.set_music_volume(self.slider_volumen.valor)
                self.game.change_state("menu")
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.game.audio.set_music_volume(self.slider_volumen.valor)
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
