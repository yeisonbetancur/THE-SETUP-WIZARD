from states.State import State
from ui.menu_classes import Button
import pygame

class MenuState(State):
    def enter(self):
        print("Entrando al menú")
        cx = self.game.pantalla.get_width() // 2
        self.btn_jugar = Button(cx - 100, 280, 200, 50, "JUGAR", self.game.fuente_chica)
        self.btn_opciones = Button(cx - 100, 350, 200, 50, "OPCIONES", self.game.fuente_chica)
        self.btn_salir = Button(cx - 100, 420, 200, 50, "SALIR", self.game.fuente_chica, (120, 50, 50), (180, 70, 70))
        self.botones = [self.btn_jugar, self.btn_opciones, self.btn_salir]


        self.game.audio.stop_music(0)

        try:
            self.background = pygame.image.load("assets/backgrounds/menu_bg.jpg").convert()
            # Escalar al tamaño de la pantalla
            self.background = pygame.transform.scale(
                self.background, 
                (self.game.pantalla.get_width(), self.game.pantalla.get_height())
            )
        except Exception as e:
            print(f"WARNING: No se pudo cargar background: {e}")
            self.background = None

        
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


        if self.background:
            pantalla.blit(self.background, (0, 0))
        else:
            # Fallback: color sólido
            pantalla.fill((30, 40, 60))
        titulo = self.game.fuente_grande.render("SETUP WIZARD", True, (0, 0, 0))
        pantalla.blit(titulo, (pantalla.get_width()//2 - titulo.get_width()//2, 100))
        for btn in self.botones:
            btn.draw(pantalla)