import pygame
from typing import Dict, Optional
from enum import Enum, auto


class MusicTrack(Enum):
    """Tracks de música disponibles"""
    GAMEPLAY = auto()


class SoundEffect(Enum):
    """Efectos de sonido disponibles"""
    HIT = auto()


class AudioManager:
    """
    Gestor centralizado de música y efectos de sonido.
    Versión simplificada: solo música de juego y sonido de hit.
    """
    
    def __init__(self):
        """Inicializa el sistema de audio"""
        # Inicializar pygame mixer
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.audio_enabled = True
        except Exception as e:
            print(f"ERROR: No se pudo inicializar el sistema de audio: {e}")
            self.audio_enabled = False
            return
        
        # Música
        self.music_tracks: Dict[MusicTrack, str] = {}
        self.current_track: Optional[MusicTrack] = None
        self.music_volume = 0.2  # Volumen por defecto (0.0 a 1.0)
        
        # Efectos de sonido
        self.sound_effects: Dict[SoundEffect, pygame.mixer.Sound] = {}
        self.sound_volume = 0.4  # Volumen por defecto para efectos
        
        # Estado
        self.music_enabled = True
        self.sounds_enabled = True
        
        # Cargar recursos
        self._load_music()
        self._load_sounds()
    
    def _load_music(self):
        """Carga los tracks de música"""
        if not self.audio_enabled:
            return
        
        music_files = {
            MusicTrack.GAMEPLAY: "assets/music/gameplay.mp3"
        }
        
        for track, filepath in music_files.items():
            try:
                # Verificar que el archivo existe
                with open(filepath, 'rb'):
                    pass
                self.music_tracks[track] = filepath
                print(f"✓ Música cargada: {track.name}")
            except FileNotFoundError:
                print(f"WARNING: No se encontró el archivo de música: {filepath}")
            except Exception as e:
                print(f"WARNING: Error cargando música {filepath}: {e}")
    
    def _load_sounds(self):
        """Carga los efectos de sonido"""
        if not self.audio_enabled:
            return
        
        sound_files = {
            SoundEffect.HIT: "assets/sounds/hit.mp3"
        }
        
        for sound, filepath in sound_files.items():
            try:
                sfx = pygame.mixer.Sound(filepath)
                sfx.set_volume(self.sound_volume)
                self.sound_effects[sound] = sfx
                print(f"✓ Sonido cargado: {sound.name}")
            except FileNotFoundError:
                print(f"WARNING: No se encontró el archivo de sonido: {filepath}")
            except Exception as e:
                print(f"WARNING: Error cargando sonido {filepath}: {e}")
    
    # ======================
    # CONTROL DE MÚSICA
    # ======================
    
    def play_music(self, track: MusicTrack, loop: bool = True, fade_in: float = 0.0):
        """
        Reproduce un track de música.
        
        Args:
            track: Track a reproducir
            loop: Si debe repetirse infinitamente
            fade_in: Segundos de fade in (0 = sin fade)
        """
        if not self.audio_enabled or not self.music_enabled:
            return
        
        if track not in self.music_tracks:
            print(f"WARNING: Track {track.name} no está cargado")
            return
        
        # Si ya está sonando este track, no hacer nada
        if self.current_track == track and pygame.mixer.music.get_busy():
            return
        
        try:
            pygame.mixer.music.load(self.music_tracks[track])
            pygame.mixer.music.set_volume(self.music_volume)
            
            loops = -1 if loop else 0
            
            if fade_in > 0:
                pygame.mixer.music.play(loops, fade_ms=int(fade_in * 1000))
            else:
                pygame.mixer.music.play(loops)
            
            self.current_track = track
            print(f"♪ Reproduciendo: {track.name}")
            
        except Exception as e:
            print(f"ERROR reproduciendo música {track.name}: {e}")
    
    def stop_music(self, fade_out: float = 0.0):
        """
        Detiene la música.
        
        Args:
            fade_out: Segundos de fade out (0 = detener inmediatamente)
        """
        if not self.audio_enabled:
            return
        
        try:
            if fade_out > 0:
                pygame.mixer.music.fadeout(int(fade_out * 1000))
            else:
                pygame.mixer.music.stop()
            
            self.current_track = None
        except Exception as e:
            print(f"ERROR deteniendo música: {e}")
    
    def pause_music(self):
        """Pausa la música"""
        if not self.audio_enabled:
            return
        
        try:
            pygame.mixer.music.pause()
            self.music_paused = True
        except Exception as e:
            print(f"ERROR pausando música: {e}")
    
    def unpause_music(self):
        """Despausa la música"""
        if not self.audio_enabled:
            return
        
        try:
            pygame.mixer.music.unpause()
            self.music_paused = False
        except Exception as e:
            print(f"ERROR despausando música: {e}")
    
    def set_music_volume(self, volume: float):
        """
        Ajusta el volumen de la música.
        
        Args:
            volume: Volumen (0.0 = silencio, 1.0 = máximo)
        """
        if not self.audio_enabled:
            return
        
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def toggle_music(self):
        """Activa/desactiva la música"""
        self.music_enabled = not self.music_enabled
        
        if not self.music_enabled:
            self.stop_music()
        
        return self.music_enabled
    
    # ======================
    # EFECTOS DE SONIDO
    # ======================
    
    def play_sound(self, sound: SoundEffect):
        """
        Reproduce un efecto de sonido.
        
        Args:
            sound: Efecto a reproducir
        """
        if not self.audio_enabled or not self.sounds_enabled:
            return
        
        if sound not in self.sound_effects:
            return
        
        try:
            self.sound_effects[sound].play()
        except Exception as e:
            print(f"ERROR reproduciendo sonido {sound.name}: {e}")
    
    def set_sound_volume(self, volume: float):
        """
        Ajusta el volumen de los efectos de sonido.
        
        Args:
            volume: Volumen (0.0 = silencio, 1.0 = máximo)
        """
        if not self.audio_enabled:
            return
        
        self.sound_volume = max(0.0, min(1.0, volume))
        
        for sound in self.sound_effects.values():
            sound.set_volume(self.sound_volume)
    
    def toggle_sounds(self):
        """Activa/desactiva los efectos de sonido"""
        self.sounds_enabled = not self.sounds_enabled
        return self.sounds_enabled
    
    # ======================
    # UTILIDADES
    # ======================
    
    def is_music_playing(self) -> bool:
        """Verifica si hay música sonando"""
        if not self.audio_enabled:
            return False
        return pygame.mixer.music.get_busy()
    
    def get_stats(self) -> dict:
        """Retorna estadísticas del sistema de audio"""
        return {
            "audio_enabled": self.audio_enabled,
            "music_enabled": self.music_enabled,
            "sounds_enabled": self.sounds_enabled,
            "music_volume": self.music_volume,
            "sound_volume": self.sound_volume,
            "current_track": self.current_track.name if self.current_track else None,
            "music_playing": self.is_music_playing(),
            "tracks_loaded": len(self.music_tracks),
            "sounds_loaded": len(self.sound_effects)
        }


# ======================
# EJEMPLO DE USO
# ======================

"""
# En tu clase Game o main:

from systems.audio_manager import AudioManager, MusicTrack, SoundEffect

class Game:
    def __init__(self):
        # ... código existente ...
        
        # Inicializar audio
        self.audio = AudioManager()
    
    # ... resto del código ...


# En PlayingState:

class PlayingState(State):
    def enter(self):
        if not self._initialized:
            self._initialize_game()
            self._initialized = True
            
            # Reproducir música de juego
            self.game.audio.play_music(MusicTrack.GAMEPLAY, loop=True, fade_in=1.0)
        else:
            # Despausar música al volver de pausa
            self.game.audio.unpause_music()
    
    def _check_projectile_collisions(self):
        # ... tu código de colisiones ...
        
        if hit:
            # Reproducir sonido de impacto
            self.game.audio.play_sound(SoundEffect.HIT)
            # ... resto del código ...


# En PauseState:

class PauseState(State):
    def enter(self):
        # Pausar música
        self.game.audio.pause_music()
    
    def exit(self):
        # Despausar música
        self.game.audio.unpause_music()
"""