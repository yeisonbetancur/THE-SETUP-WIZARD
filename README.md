# THE SETUP WIZARD

Juego de hechizos elementales controlado por gestos de mano o teclado. Combina diferentes elementos para crear hechizos poderosos y derrota oleadas de enemigos.

---

## 📋 Requisitos del Sistema

- **Python 3.8 o superior, menor a 3.13 por compatibilidad con mediapipe**
- **Cámara web** (opcional, solo para control por gestos)
- **Sistema Operativo:** Windows, macOS o Linux

---

## 🚀 Instalación

### 1. Clonar o descargar el proyecto

```bash
git clone <url-del-repositorio>
cd mi_juego
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

O manualmente:

```bash
pip install pygame mediapipe opencv-python numpy
```

### 3. Verificar estructura de carpetas

Asegúrate de tener estas carpetas (se crearán automáticamente si faltan):

```
mi_juego/
├── main.py
├── config/
├── systems/
├── entities/
├── states/
└── assets/          # ← Carpeta para recursos (opcional)
    ├── sprites/
    ├── music/
    ├── sounds/
    └── backgrounds/
```

---

## ▶️ Ejecutar el Juego

### Con control por gestos (requiere cámara):
```bash
python main.py
```

### Solo con teclado (sin cámara):
Edita `main.py` y cambia:
```python
gestos_activos=False
```
Luego ejecuta:
```bash
python main.py
```

---

## 🎮 Controles

### 🤚 Control por Gestos (Cámara)

Muestra estos gestos frente a la cámara:

| Gesto | Acción | Elemento |
|-------|--------|----------|
| **Paz** ✌️ | Crear círculo de Hielo | ❄️ |
| **Rock** 🤘 | Crear círculo de Fuego | 🔥 |
| **Mano Abierta** ✋ | Crear círculo de Rayo | ⚡ |
| **Pulgar Arriba** 👍 | Crear círculo de Tierra | 🪨 |
| **Shaka** 🤙 | Crear círculo de Agua | 💧 |
| **Puño Cerrado** 👊 | Lanzar hechizo | 💥 |

### ⌨️ Control por Teclado (Debug/Alternativo)

| Tecla | Acción |
|-------|--------|
| **1** | Crear círculo de Fuego |
| **2** | Crear círculo de Hielo |
| **3** | Crear círculo de Rayo |
| **4** | Crear círculo de Tierra |
| **5** | Crear círculo de Agua |
| **SPACE** | Lanzar hechizo |
| **ESC** | Pausar juego |
| **F3** | Mostrar estadísticas (debug) |
| **Q/W/E** | Spawnear enemigos (testing) |

---

## 🎯 Cómo Jugar

### Mecánica Principal

1. **Crea círculos elementales** con gestos o teclado (máximo 2 simultáneos)
2. **Lanza hechizos** con el gesto de puño o SPACE
3. El hechizo se determina por los círculos activos:
   - **0 círculos** → Proyectil neutral
   - **1 círculo** → Hechizo elemental simple
   - **2 círculos** → Hechizo combo híbrido

### Sistema de Elementos

**Elementos básicos:**
- 🔥 **Fuego** - Alto daño, quema enemigos
- ❄️ **Hielo** - Ralentiza y congela
- ⚡ **Rayo** - Atraviesa múltiples enemigos
- 🪨 **Tierra** - Aturde enemigos
- 💧 **Agua** - Empuja enemigos

**Combos de 2 elementos:**
- 🔥+❄️ = **Vapor** (confunde enemigos)
- 🔥+⚡ = **Explosión** (daño en área)
- 🔥+🪨 = **Lava** (daño continuo en suelo)
- 🔥+💧 = **Vapor Curativo** (cura al jugador)
- ❄️+⚡ = **Tormenta de Hielo** (múltiples proyectiles)
- ❄️+🪨 = **Avalancha** (proyectil masivo)
- ❄️+💧 = **Ventisca** (ola congelante)
- ⚡+🪨 = **Temblor** (ondas sísmicas)
- ⚡+💧 = **Electrocución** (cadena eléctrica)
- 🪨+💧 = **Lodo** (ralentiza mucho)

### Sistema de Trayectorias

Cada hechizo tiene su propia trayectoria:
- **→ Frontal:** Rápida, alto daño
- **↗ Aérea:** Arco parabólico, efectiva vs enemigos voladores
- **↘ Baja:** Ras del suelo, efectiva vs enemigos terrestres

### Enemigos

- **Slime** 🟢 - Básico, débil a fuego y rayo
- **Esqueleto** 💀 - Resistente, débil a tierra
- **Murciélago** 🦇 - Vuela alto, **solo vulnerable a ataques aéreos**

### Objetivo

- **Sobrevivir 8 oleadas** de enemigos
- **3 vidas** - Pierdes 1 vida si un enemigo te toca
- Acumula puntos derrotando enemigos

---

## 🎨 Assets Opcionales

El juego funciona **sin assets** usando gráficos procedurales. Para mejorar la experiencia visual:

### Sprites (PNG)

```
assets/sprites/
├── player/
│   ├── idle_0.png, idle_1.png, ...     # Animación idle
│   ├── fuego.png, hielo.png, ...       # Animación de cast por elemento
├── enemies/
│   ├── slime/frame_0.png, ...
│   ├── esqueleto/frame_0.png, ...
│   └── murcielago/frame_0.png, ...
└── spells/
    ├── fuego/frame_0.png, ...
    └── ...
```

### Audio (MP3/WAV)

```
assets/
├── music/
│   └── gameplay.mp3    # Música durante el juego
└── sounds/
    └── hit.wav         # Sonido de impacto
```

### Fondos (PNG/JPG)

```
assets/backgrounds/
└── game_bg.png         # Fondo del juego
```

---

## 🐛 Solución de Problemas

### Error: "No module named 'pygame'"
```bash
pip install pygame mediapipe opencv-python numpy
```

### La cámara no se detecta
- Verifica que la cámara esté conectada y funcionando
- Cierra otras aplicaciones que usen la cámara (Zoom, Teams, etc.)
- Usa modo teclado: `gestos_activos=False` en `main.py`

### El juego va muy lento
- **Desactiva gestos:** Cambia `gestos_activos=False` en `main.py`
- Cierra aplicaciones en segundo plano
- Reduce la resolución del juego (edita `main.py`)

### No se ven los sprites/No hay música
- **Esto es normal** - El juego funciona sin assets
- Los gráficos procedurales se usan automáticamente
- Para agregar assets, sigue la estructura de carpetas arriba

### Error de MediaPipe en macOS
```bash
pip install --upgrade mediapipe
```

### Pantalla negra al iniciar
- Espera unos segundos (carga de MediaPipe)
- Verifica que Python 3.8+ esté instalado: `python --version`

---

## 🛠️ Configuración Avanzada

### Desactivar música/sonidos

En tu código, después de crear el `AudioManager`:

```python
game.audio.toggle_music()   # Desactivar música
game.audio.toggle_sounds()  # Desactivar sonidos
```

### Ajustar volumen

```python
game.audio.set_music_volume(0.3)   # 30% volumen música
game.audio.set_sound_volume(0.5)   # 50% volumen efectos
```

### Cambiar tamaño de ventana

En `main.py`:
```python
pantalla = pygame.display.set_mode((1920, 1080))  # Full HD
```

---

## 📦 Dependencias

- **pygame** (>=2.5.0) - Motor de juego
- **mediapipe** (>=0.10.0) - Detección de gestos
- **opencv-python** (>=4.8.0) - Procesamiento de video
- **numpy** (>=1.24.0) - Cálculos numéricos

---

---

## 🤝 Créditos

Desarrollado por Sarasvati Dallos Velez Y Yeison Betancur Delgado

---

## 🎮 ¡A Jugar!

```bash
python main.py
```

¡Disfruta combinando elementos y derrotando enemigos! 🔥❄️⚡🪨💧
