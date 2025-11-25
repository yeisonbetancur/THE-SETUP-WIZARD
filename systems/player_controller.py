"""
Sistema de Control del Jugador
Maneja input (teclado/gestos) y lanzamiento de hechizos
"""
import pygame
from config.enums import Element, SpellType


class PlayerController:
    """Maneja el input del jugador y la lógica de lanzamiento de hechizos"""
    
    def __init__(self, spell_casting_system, animation_controller):
        """
        Args:
            spell_casting_system: Sistema de creación de hechizos
            animation_controller: Controlador de animaciones del jugador
        """
        self.spell_casting = spell_casting_system
        self.animation = animation_controller
        
        # Estado de gestos
        self.gesto_anterior = "NINGUNO"
        self.ultimo_elemento_lanzado = None
        
        # Callbacks
        self.on_spell_cast = None  # Callback(spell_type, success) -> None
        self.on_circle_created = None  # Callback(element) -> None
        
    def handle_keyboard_input(self, eventos):
        """
        Maneja input de teclado (para testing/debug)
        
        Args:
            eventos: Lista de eventos de pygame
            
        Returns:
            dict: Acciones realizadas {
                'circles_created': [Element, ...],
                'spell_cast': bool
            }
        """
        actions = {
            'circles_created': [],
            'spell_cast': False
        }
        
        for evento in eventos:
            if evento.type == pygame.KEYDOWN:
                # Crear círculos elementales
                if evento.key == pygame.K_1:
                    self._create_circle(Element.FUEGO)
                    actions['circles_created'].append(Element.FUEGO)
                    
                elif evento.key == pygame.K_2:
                    self._create_circle(Element.HIELO)
                    actions['circles_created'].append(Element.HIELO)
                    
                elif evento.key == pygame.K_3:
                    self._create_circle(Element.RAYO)
                    actions['circles_created'].append(Element.RAYO)
                    
                elif evento.key == pygame.K_4:
                    self._create_circle(Element.TIERRA)
                    actions['circles_created'].append(Element.TIERRA)
                    
                elif evento.key == pygame.K_5:
                    self._create_circle(Element.AGUA)
                    actions['circles_created'].append(Element.AGUA)
                    
                # Lanzar hechizo
                elif evento.key == pygame.K_SPACE:
                    success = self._cast_spell()
                    actions['spell_cast'] = success
        
        return actions
    
    def handle_gesture_input(self, gesture_detector, dt):
        """
        Maneja input de gestos por cámara
        
        Args:
            gesture_detector: Detector de gestos con cámara
            dt: Delta time
            
        Returns:
            dict: Acciones realizadas {
                'circles_created': [Element, ...],
                'spell_cast': bool,
                'gesture': str
            }
        """
        actions = {
            'circles_created': [],
            'spell_cast': False,
            'gesture': 'NINGUNO'
        }
        
        # Actualizar detector de gestos
        resultado = gesture_detector.actualizar(dt)
        if not resultado:
            return actions
        
        gesto_confirmado = gesture_detector.gesto_confirmado
        actions['gesture'] = gesto_confirmado
        
        # Solo procesar si cambió el gesto (evitar spam)
        if gesto_confirmado == self.gesto_anterior:
            return actions
        
        # Mapeo de gestos a elementos
        gesture_to_element = {
            "PAZ": Element.HIELO,        # ✌️
            "ROCK": Element.FUEGO,       # 🤘
            "ABIERTA": Element.RAYO,     # ✋
            "THUMBS_UP": Element.TIERRA, # 👍
            "SHAKA": Element.AGUA,       # 🤙
        }
        
        # Crear círculo si es un gesto de elemento
        if gesto_confirmado in gesture_to_element:
            elemento = gesture_to_element[gesto_confirmado]
            self._create_circle(elemento)
            actions['circles_created'].append(elemento)
            self.gesto_anterior = gesto_confirmado
        
        # Lanzar hechizo con puño
        elif gesto_confirmado == "PUÑO":  # 👊
            success = self._cast_spell()
            actions['spell_cast'] = success
            self.gesto_anterior = gesto_confirmado
        
        # Resetear gesto anterior si vuelve a NINGUNO
        elif gesto_confirmado == "NINGUNO":
            self.gesto_anterior = "NINGUNO"
        
        return actions
    
    def _create_circle(self, elemento):
        """
        Crea un círculo mágico del elemento especificado
        
        Args:
            elemento: Element enum
        """
        self.spell_casting.create_circle(elemento)
        
        # Callback
        if self.on_circle_created:
            self.on_circle_created(elemento)
    
    def _cast_spell(self):
        """
        Intenta lanzar un hechizo con los círculos activos
        
        Returns:
            bool: True si el hechizo se lanzó exitosamente
        """
        # Obtener información del próximo hechizo
        spell_info = self.spell_casting.get_next_spell_info()
        
        if spell_info:
            # Determinar elemento para la animación
            elemento_anim = self._get_animation_element(spell_info)
            
            # Reproducir animación de cast
            self._play_cast_animation(elemento_anim)
        
        # Callback
        if self.on_spell_cast:
            spell_type = spell_info["spell_type"] if spell_info else None
            self.on_spell_cast(spell_type, spell_info is not None)
        
        return spell_info is not None
    
    def cast_spell_at_position(self, x, y):
        """
        Lanza un hechizo en una posición específica
        
        Args:
            x: Posición X
            y: Posición Y
            
        Returns:
            bool: True si el hechizo se lanzó exitosamente
        """
        # Obtener información del hechizo
        spell_info = self.spell_casting.get_next_spell_info()
        
        if spell_info:
            # Determinar elemento para animación
            elemento_anim = self._get_animation_element(spell_info)
            self._play_cast_animation(elemento_anim)
        
        # Lanzar hechizo
        success = self.spell_casting.cast_spell(x, y)
        
        # Callback
        if self.on_spell_cast:
            spell_type = spell_info["spell_type"] if spell_info else None
            self.on_spell_cast(spell_type, success)
        
        return success
    
    def _play_cast_animation(self, elemento):
        """
        Reproduce la animación de lanzar hechizo según el elemento
        
        Args:
            elemento: Element enum
        """
        element_to_anim = {
            Element.FUEGO: "cast_fuego",
            Element.HIELO: "cast_hielo",
            Element.RAYO: "cast_rayo",
            Element.TIERRA: "cast_tierra",
            Element.AGUA: "cast_agua",
            Element.NEUTRAL: "cast_neutral"
        }
        
        anim_name = element_to_anim.get(elemento, "cast_neutral")
        self.animation.play(anim_name, reset=True)
        self.ultimo_elemento_lanzado = elemento
    
    def _get_animation_element(self, spell_info):
        """
        Determina qué animación de elemento usar según el hechizo
        Para combos, usa el primer elemento
        
        Args:
            spell_info: Diccionario con info del hechizo
            
        Returns:
            Element: Elemento para la animación
        """
        spell_type = spell_info["spell_type"]
        elements = spell_info.get("elements", [])
        
        # Mapeo de hechizos básicos a elementos
        basic_spells = {
            SpellType.FUEGO: Element.FUEGO,
            SpellType.HIELO: Element.HIELO,
            SpellType.RAYO: Element.RAYO,
            SpellType.TIERRA: Element.TIERRA,
            SpellType.AGUA: Element.AGUA,
            SpellType.NEUTRAL: Element.NEUTRAL
        }
        
        # Si es un hechizo básico, usar su elemento
        if spell_type in basic_spells:
            return basic_spells[spell_type]
        
        # Si es un combo, usar el primer elemento
        if elements:
            return elements[0]
        
        # Fallback
        return Element.NEUTRAL
    
    def update(self, dt):
        """
        Actualiza el controlador
        
        Args:
            dt: Delta time
        """
        # Actualizar animación
        self.animation.update(dt)
        
        # Volver a idle cuando termine la animación de cast
        current_anim = self.animation.get_current_animation_name()
        if current_anim and current_anim.startswith("cast_"):
            if self.animation.current_animation.is_finished():
                self.animation.play("idle")
    
    def get_cooldown_info(self):
        """
        Obtiene información del cooldown actual
        
        Returns:
            dict: Info del cooldown del sistema de hechizos
        """
        return self.spell_casting.get_cooldown_info()
    
    def get_active_circles_info(self):
        """
        Obtiene información de círculos activos
        
        Returns:
            dict: Info de círculos del sistema de hechizos
        """
        return self.spell_casting.get_circle_info()
    
    def clear(self):
        """Limpia el estado del controlador"""
        self.gesto_anterior = "NINGUNO"
        self.ultimo_elemento_lanzado = None