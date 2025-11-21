from State import State
import pygame

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
            resultado = self.game.gesture_detector.actualizar(dt)
            if resultado:
                gesto_confirmado = self.game.gesture_detector.gesto_confirmado
                
                # Mover el círculo con la posición de la mano
                if gesto_confirmado == "ABIERTA":
                    detector = self.game.gesture_detector
                    # Escalar velocidad (multiplicador para ajustar sensibilidad)
                    multiplicador_velocidad = 5000

                    vel_x = detector.velocidad_mano[0] * multiplicador_velocidad * dt
                    vel_y = detector.velocidad_mano[1] * multiplicador_velocidad * dt

                    self.pos[0] += -vel_x
                    self.pos[1] += vel_y

                    # Mantener dentro de los límites de la pantalla
                    ancho = self.game.pantalla.get_width()
                    alto = self.game.pantalla.get_height()
                    self.pos[0] = max(20, min(self.pos[0], ancho - 20))
                    self.pos[1] = max(20, min(self.pos[1], alto - 20))
                
                # Cambiar color según el gesto
                if gesto_confirmado != self.gesto_anterior:
                    if gesto_confirmado == "PAZ":
                        self.color = (0, 255, 0)
                        self.puntos += 1
                    elif gesto_confirmado == "ROCK":
                        self.color = (255, 0, 255)
                        self.puntos += 1
                    elif gesto_confirmado == "SHAKA":
                        self.color = (0, 255, 255)
                        self.puntos += 1
                    elif gesto_confirmado == "PUÑO":
                        self.color = (255, 0, 0)
                    elif gesto_confirmado == "ABIERTA":
                        self.color = (255, 200, 0)
                        
                    self.gesto_anterior = gesto_confirmado
                    
    def draw(self, pantalla):
        pantalla.fill((50, 80, 50))
        
        # Dibujar círculo del jugador
        pygame.draw.circle(pantalla, self.color, (int(self.pos[0]), int(self.pos[1])), 20)
        
        # Información en pantalla
        y_offset = 10
        controles = "WASD mover | ESC pausa"
        if self.game.gestos_activos:
            gesto = self.game.gesture_detector.gesto_confirmado
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