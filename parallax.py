import pygame

class ParallaxLayer:
    def __init__(self, ruta, velocidad, pantalla):
        self.pantalla = pantalla
        self.velocidad = velocidad
        
        # cargar imagen
        self.image = pygame.image.load(ruta).convert_alpha()
        self.image = pygame.transform.scale(
            self.image,
            (pantalla.get_width(), pantalla.get_height())
        )

        # posiciones de las dos copias para scroll infinito
        self.x1 = 0
        self.x2 = self.image.get_width()

    def update(self):
        # si la capa no se mueve, no tocar posiciones
        if self.velocidad == 0:
            return

        ancho = self.image.get_width()

        # mover ambas imágenes
        self.x1 -= self.velocidad
        self.x2 -= self.velocidad

        # ========== MOVIMIENTO IZQUIERDA (velocidad positiva) ==========
        if self.velocidad > 0:
            if self.x1 <= -ancho:
                self.x1 = self.x2 + ancho
            if self.x2 <= -ancho:
                self.x2 = self.x1 + ancho

        # ========== MOVIMIENTO DERECHA (velocidad negativa) ==========
        else:
            if self.x1 >= ancho:
                self.x1 = self.x2 - ancho
            if self.x2 >= ancho:
                self.x2 = self.x1 - ancho

    def draw(self):
        self.pantalla.blit(self.image, (self.x1, 0))
        self.pantalla.blit(self.image, (self.x2, 0))
