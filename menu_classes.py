import pygame

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