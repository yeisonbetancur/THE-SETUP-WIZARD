import mediapipe as mp
import math
import numpy as np
import cv2


class GestureDetector:
    def __init__(self, tiempo_confirmacion=0.5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )
        
        self.mp_draw = mp.solutions.drawing_utils
        self.cap = None
        self.ultimo_gesto = "NINGUNO"
        self.gesto_confirmado = "NINGUNO"
        self.posicion_mano = (0, 0)  # Posición normalizada (0-1)
        self.posicion_anterior = None  # Nueva variable
        self.velocidad_mano = (0, 0)  # Nueva variable
        self.activo = False
        
        # Sistema de confirmación de gestos
        self.tiempo_confirmacion = tiempo_confirmacion  # Segundos para confirmar
        self.gesto_actual = "NINGUNO"
        self.tiempo_mantenido = 0.0
        self.progreso_confirmacion = 0.0  # 0.0 a 1.0
        
    def iniciar_camara(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            self.activo = True
            
    def detener_camara(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            self.activo = False
            
    def distancia(self, p1, p2):
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)
    
    def dedos_extendidos(self, landmarks):
        dedos = []
        # Pulgar: comparamos X
        dedos.append(landmarks[4].x > landmarks[3].x)
        # Índice -> meñique: comparamos Y
        for tip, knuckle in [(8,6),(12,10),(16,14),(20,18)]:
            dedos.append(landmarks[tip].y < landmarks[knuckle].y)
        return dedos
    
    def detectar_gesto(self, landmarks):
        dedos = self.dedos_extendidos(landmarks)
        pulgar, ind, med, anu, men = dedos
        
        if sum(dedos) == 0:
            return "PUÑO"
        if sum(dedos) == 5:
            return "ABIERTA"
        if ind and med and not anu and not men:
            return "PAZ"
        if ind and men and not med and not anu:
            return "ROCK"
        if pulgar and men and not ind and not med and not anu:
            return "SHAKA"
        if pulgar and not men and not ind and not med and not anu:
            return "THUMBS_UP"
        return "DESCONOCIDO"
    
    def actualizar(self, dt=0.016):
        if not self.activo or self.cap is None:
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            return None
            
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            landmarks = hand_landmarks.landmark
            
            # Detectar gesto actual
            gesto_detectado = self.detectar_gesto(landmarks)
            
            # Sistema de confirmación
            if gesto_detectado == self.gesto_actual:
                # Mantiene el mismo gesto, incrementar tiempo
                self.tiempo_mantenido += dt
                self.progreso_confirmacion = min(1.0, self.tiempo_mantenido / self.tiempo_confirmacion)
                
                # Si se mantiene el tiempo suficiente, confirmar el gesto
                if self.tiempo_mantenido >= self.tiempo_confirmacion:
                    if self.gesto_confirmado != gesto_detectado:
                        self.gesto_confirmado = gesto_detectado
                        print(f"✓ Gesto confirmado: {self.gesto_confirmado}, tiempo mantenido: {self.tiempo_mantenido}")
            else:
                # Cambió de gesto, reiniciar contador
                self.gesto_actual = gesto_detectado
                self.tiempo_mantenido = 0.0
                self.progreso_confirmacion = 0.0
            
            self.ultimo_gesto = gesto_detectado
            
            # Obtener posición de la palma (landmark 9)
            palma = landmarks[9]
            nueva_posicion = (palma.x, palma.y)

            # Calcular velocidad
            if self.posicion_anterior is not None:
                delta_x = nueva_posicion[0] - self.posicion_anterior[0]
                delta_y = nueva_posicion[1] - self.posicion_anterior[1]
                self.velocidad_mano = (delta_x, delta_y)
            else:
                self.velocidad_mano = (0, 0)

            self.posicion_mano = nueva_posicion
            self.posicion_anterior = nueva_posicion
            
            return frame, hand_landmarks
        else:
            # No hay mano detectada, reiniciar
            self.ultimo_gesto = "NINGUNO"
            self.gesto_actual = "NINGUNO"
            self.tiempo_mantenido = 0.0
            self.progreso_confirmacion = 0.0
            
        return frame, None
