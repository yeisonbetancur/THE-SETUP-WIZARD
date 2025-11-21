import cv2
import mediapipe as mp
import math

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1,
                       min_detection_confidence=0.6,
                       min_tracking_confidence=0.6)
mp_draw = mp.solutions.drawing_utils

# --------------------------
# Funciones auxiliares
# --------------------------

def distancia(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 +
                     (p1.y - p2.y)**2 +
                     (p1.z - p2.z)**2)

def dedos_extendidos(landmarks):
    dedos = []
    # Pulgar: comparamos X
    dedos.append(landmarks[4].x > landmarks[3].x)
    # Índice -> meñique: comparamos Y
    for tip, knuckle in [(8,6),(12,10),(16,14),(20,18)]:
        dedos.append(landmarks[tip].y < landmarks[knuckle].y)
    return dedos  # [pulgar, índice, medio, anular, meñique]



# --------------------------
# Detector de gestos
# --------------------------

def detectar_gesto(landmarks):

    dedos = dedos_extendidos(landmarks)
    pulgar, ind, med, anu, men = dedos
    if sum(dedos) == 0:
        return "PUÑO"

    # Mano abierta: todos extendidos
    if sum(dedos) == 5:
        return "ABIERTA"

    # Símbolo de paz: índice + medio extendidos
    if ind and med and not anu and not men:
        return "PAZ"

    # Rock: índice + meñique extendidos
    if ind and men and not med and not anu:
        return "ROCK"

    # Shaka: pulgar + meñique extendidos
    if pulgar and men and not ind and not med and not anu:
        return "SHKA"

    return "DESCONOCIDO"



cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        gesto = detectar_gesto(hand_landmarks.landmark)

        cv2.putText(frame, gesto, (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

    cv2.imshow("Camara", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
