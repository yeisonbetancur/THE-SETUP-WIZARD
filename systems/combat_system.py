"""
Sistema de Combate y Colisiones
Maneja todas las interacciones de daño entre hechizos y enemigos
"""
from config.enums import Element, EffectType, TrajectoryType, SpellType
from config.spell_data import SPELL_DATABASE


class CombatSystem:
    """Maneja colisiones, daño y efectos de combate"""
    
    def __init__(self, spell_system, enemy_manager, audio_manager):
        """
        Args:
            spell_system: Sistema de hechizos (proyectiles y áreas)
            enemy_manager: Gestor de enemigos
            audio_manager: Gestor de audio para efectos de sonido
        """
        self.spell_system = spell_system
        self.enemy_manager = enemy_manager
        self.audio = audio_manager
        
        # Callbacks para eventos de combate
        self.on_enemy_hit = None  # Callback(enemy, damage, element) -> None
        self.on_projectile_hit = None  # Callback(projectile, enemy) -> None
        self.on_area_hit = None  # Callback(area_effect, enemy) -> None
        
    def update(self, dt):
        """
        Actualiza el sistema de combate
        Verifica todas las colisiones entre hechizos y enemigos
        
        Args:
            dt: Delta time
            
        Returns:
            dict: Estadísticas del frame {
                'projectile_hits': int,
                'area_hits': int,
                'total_damage': int,
                'enemies_killed': int
            }
        """
        stats = {
            'projectile_hits': 0,
            'area_hits': 0,
            'total_damage': 0,
            'enemies_killed': 0
        }
        
        # Verificar colisiones de proyectiles
        projectile_stats = self._check_projectile_collisions()
        stats['projectile_hits'] = projectile_stats['hits']
        stats['total_damage'] += projectile_stats['damage']
        stats['enemies_killed'] += projectile_stats['kills']
        
        # Verificar colisiones de efectos de área
        area_stats = self._check_area_collisions()
        stats['area_hits'] = area_stats['hits']
        stats['total_damage'] += area_stats['damage']
        stats['enemies_killed'] += area_stats['kills']
        
        return stats
    
    def _check_projectile_collisions(self):
        """
        Verifica colisiones entre proyectiles activos y enemigos
        
        Returns:
            dict: {'hits': int, 'damage': int, 'kills': int}
        """
        stats = {'hits': 0, 'damage': 0, 'kills': 0}
        
        for projectile in self.spell_system.get_active_projectiles():
            # Verificar que el proyectil esté activo y tenga datos
            if not projectile.state.active or projectile.state.spell_data is None:
                continue
            
            # Verificar colisión con cada enemigo
            for enemy in self.enemy_manager.get_active_enemies():
                if not projectile.rect.colliderect(enemy.rect):
                    continue
                
                # Verificar si el proyectil puede golpear (cooldown interno)
                if not projectile.can_hit_enemy():
                    continue
                
                # Obtener datos del hechizo
                elemento = self._get_element_from_spell(projectile.state.spell_data)
                trayectoria = projectile.state.trajectory_type
                damage = projectile.state.spell_data.daño
                
                # Aplicar daño
                was_alive = enemy.hp > 0
                hit_success = enemy.take_damage(damage, elemento, trayectoria)
                
                if hit_success:
                    # Reproducir sonido de impacto
                    from systems.audio_manager import SoundEffect
                    self.audio.play_sound(SoundEffect.HIT)
                    
                    # Actualizar estadísticas
                    stats['hits'] += 1
                    stats['damage'] += damage
                    
                    # Verificar si el enemigo murió
                    if was_alive and enemy.hp <= 0:
                        stats['kills'] += 1
                    
                    # Aplicar efectos de estado (quemadura, congelación, etc.)
                    self._apply_spell_effects(enemy, projectile.state.spell_data)
                    
                    # Manejar explosiones de área
                    if projectile.state.spell_data.efecto == EffectType.AREA_EXPLOSION:
                        explosion_stats = self._handle_area_explosion(
                            projectile.state.x,
                            projectile.state.y,
                            projectile.state.spell_data
                        )
                        stats['damage'] += explosion_stats['damage']
                        stats['kills'] += explosion_stats['kills']
                    
                    # Callback de impacto
                    if self.on_projectile_hit:
                        self.on_projectile_hit(projectile, enemy)
                    
                    # Verificar si el proyectil se destruye al impactar
                    if not projectile.on_hit_enemy():
                        projectile.deactivate()
                        break  # El proyectil ya no existe, salir del loop de enemigos
        
        return stats
    
    def _check_area_collisions(self):
        """
        Verifica colisiones entre efectos de área activos y enemigos
        
        Returns:
            dict: {'hits': int, 'damage': int, 'kills': int}
        """
        stats = {'hits': 0, 'damage': 0, 'kills': 0}
        
        for area_effect in self.spell_system.get_active_area_effects():
            if not area_effect.state.active:
                continue
            
            for enemy in self.enemy_manager.get_active_enemies():
                # Verificar si el enemigo está dentro del área
                if not area_effect.rect.colliderect(enemy.rect):
                    continue
                
                # Verificar cooldown de tick (para evitar daño múltiple instantáneo)
                if not area_effect.can_affect_enemy(id(enemy)):
                    continue
                
                # Obtener elemento y daño
                elemento = self._get_element_from_spell(area_effect.state.spell_data)
                damage = area_effect.get_damage()
                
                # Aplicar daño o curación
                if damage > 0:  # Daño normal
                    was_alive = enemy.hp > 0
                    hit_success = enemy.take_damage(damage, elemento, TrajectoryType.FRONTAL)
                    
                    if hit_success:
                        from systems.audio_manager import SoundEffect
                        self.audio.play_sound(SoundEffect.HIT)
                        
                        stats['hits'] += 1
                        stats['damage'] += damage
                        
                        if was_alive and enemy.hp <= 0:
                            stats['kills'] += 1
                        
                        # Aplicar efectos de estado
                        self._apply_spell_effects(enemy, area_effect.state.spell_data)
                        
                        # Callback
                        if self.on_area_hit:
                            self.on_area_hit(area_effect, enemy)
                
                elif damage < 0:  # Curación (ej: Vapor Caliente)
                    # TODO: Implementar curación del jugador si es necesario
                    pass
                
                # Registrar que este enemigo fue afectado (para cooldown de tick)
                area_effect.on_affect_enemy(id(enemy))
        
        return stats
    
    def _apply_spell_effects(self, enemy, spell_data):
        """
        Aplica efectos de estado a un enemigo según el tipo de hechizo
        
        Args:
            enemy: Enemigo objetivo
            spell_data: Datos del hechizo (de SPELL_DATABASE)
        """
        efecto = spell_data.efecto
        params = spell_data.efecto_params
        
        if efecto == EffectType.SLOW:
            # Ralentizar movimiento
            enemy.apply_slow(
                params.get("slow_factor", 0.5),  # 50% de velocidad por defecto
                params.get("duracion", 2.0)
            )
        
        elif efecto == EffectType.STUN:
            # Aturdir (paralizar)
            enemy.apply_stun(
                params.get("duracion", 1.0), 
                is_freeze=False
            )
        
        elif efecto == EffectType.DOT:
            # Daño sobre tiempo (ej: quemadura)
            enemy.apply_dot(
                params.get("tick_damage", 2),
                params.get("duracion", 3.0),
                params.get("tick_rate", 0.5)
            )
        
        elif efecto == EffectType.FREEZE:
            # Congelar = stun con visual especial
            enemy.apply_stun(
                params.get("duracion_congelacion", 2.0),
                is_freeze=True
            )
        
        elif efecto == EffectType.KNOCKBACK:
            # Empujar hacia atrás
            enemy.apply_knockback(
                params.get("fuerza", 200)
            )
        
        elif efecto == EffectType.CONFUSION:
            # Confundir (movimiento errático)
            enemy.apply_confusion(
                params.get("duracion", 4.0)
            )
    
    def _handle_area_explosion(self, explosion_x, explosion_y, spell_data):
        """
        Maneja explosiones de área (daño radial)
        
        Args:
            explosion_x: Posición X de la explosión
            explosion_y: Posición Y de la explosión
            spell_data: Datos del hechizo explosivo
            
        Returns:
            dict: {'damage': int, 'kills': int}
        """
        stats = {'damage': 0, 'kills': 0}
        
        params = spell_data.efecto_params
        radio = params.get("radio_explosion", 100)
        daño_centro = params.get("daño_centro", 25)
        daño_borde = params.get("daño_borde", 10)
        
        elemento = self._get_element_from_spell(spell_data)
        
        # Encontrar todos los enemigos en el radio
        for enemy in self.enemy_manager.get_active_enemies():
            # Calcular distancia euclidiana
            dx = enemy.x - explosion_x
            dy = enemy.y - explosion_y
            distancia = (dx**2 + dy**2)**0.5
            
            if distancia <= radio:
                # Calcular daño según distancia (interpolación lineal)
                if distancia == 0:
                    daño = daño_centro
                else:
                    # Factor de distancia: 1.0 en el centro, 0.0 en el borde
                    factor = 1 - (distancia / radio)
                    daño = int(daño_borde + (daño_centro - daño_borde) * factor)
                
                # Aplicar daño
                was_alive = enemy.hp > 0
                enemy.take_damage(daño, elemento, TrajectoryType.FRONTAL)
                
                stats['damage'] += daño
                
                if was_alive and enemy.hp <= 0:
                    stats['kills'] += 1
        
        return stats
    
    def _get_element_from_spell(self, spell_data):
        """
        Determina el elemento principal de un hechizo
        
        Args:
            spell_data: Datos del hechizo
            
        Returns:
            Element: Elemento del hechizo
        """
        # Mapeo de SpellType a Element
        spell_to_element = {
            SpellType.NEUTRAL: Element.NEUTRAL,
            SpellType.FUEGO: Element.FUEGO,
            SpellType.HIELO: Element.HIELO,
            SpellType.RAYO: Element.RAYO,
            SpellType.TIERRA: Element.TIERRA,
            SpellType.AGUA: Element.AGUA,
            
            # Combos - usar elemento dominante
            SpellType.VAPOR: Element.FUEGO,
            SpellType.EXPLOSION: Element.FUEGO,
            SpellType.LAVA: Element.FUEGO,
            SpellType.VAPOR_CALIENTE: Element.FUEGO,
            SpellType.TORMENTA_HIELO: Element.HIELO,
            SpellType.AVALANCHA: Element.HIELO,
            SpellType.VENTISCA: Element.HIELO,
            SpellType.TEMBLOR: Element.TIERRA,
            SpellType.ELECTROCUCION: Element.RAYO,
            SpellType.BARRO: Element.TIERRA,
        }
        
        # Buscar por nombre del hechizo en la base de datos
        for spell_type, element in spell_to_element.items():
            if spell_data.nombre == SPELL_DATABASE[spell_type].nombre:
                return element
        
        # Fallback
        return Element.NEUTRAL
    
    def get_stats(self):
        """
        Obtiene estadísticas del sistema de combate
        
        Returns:
            dict: Estadísticas actuales
        """
        return {
            'active_projectiles': len(list(self.spell_system.get_active_projectiles())),
            'active_areas': len(list(self.spell_system.get_active_area_effects())),
            'active_enemies': len(list(self.enemy_manager.get_active_enemies()))
        }