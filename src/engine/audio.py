"""Música por estado e efeitos compartilhados, carregados uma vez por partida."""

import logging
from pathlib import Path

import pygame


ASSET_ROOT = Path(__file__).resolve().parents[2] / "assets" / "Audio"
MUSIC = {
    "menu": "music/Menu/MusicMenu.ogg",
    "background": "music/Background/BackGroundMusic.ogg",
    "miniboss": "music/MiniBoss/MiniBossMusic.ogg",
    "finalboss": "music/FinalBoss/Final.ogg",
}
MUSIC_START = {"miniboss": 43.0}  # segundos em que a faixa começa a tocar
SFX = {
    "player_punch": "sfx/Apolo/PlayersPunch.ogg",
    "hadouken": "sfx/Apolo/HadoukenSoundEffect.ogg",
    "player_dash": "sfx/Dash/Dash.ogg",
    "powerup": "sfx/Health/PowerUp.ogg",
    "player_damage_1": "sfx/Apolo/AudioDano01.ogg",
    "player_damage_2": "sfx/Apolo/AudioDano02.ogg",
    "player_death": "sfx/Apolo/ApoloDeath.ogg",
    "enemy_death": "sfx/Enemy/EnemyDeath.ogg",
    "menu_navigation": "sfx/Menu/Menu.ogg",
    "mrblack_attack": "sfx/MrBlack/BossEffect.ogg",
    "mrblack_special": "sfx/MrBlack/SPA.ogg",
    "mrblack_death": "sfx/MrBlack/MrBlackDeath.ogg",
    "professor_attack": "sfx/Professor/BossEffect.ogg",
    "professor_special": "sfx/Professor/SPA.ogg",
    "professor_death": "sfx/Professor/GuyDeath.ogg",
    "game_over": "sfx/Ending/Game_Over.ogg",
    "victory": "sfx/Ending/Victory_Tune.ogg",
}
LOGGER = logging.getLogger(__name__)


class AudioManager:
    def __init__(self, music_volume=0.4, sfx_volume=1.0):
        self.music_volume = max(0.0, min(1.0, music_volume))
        self.sfx_volume = max(0.0, min(1.0, sfx_volume))
        self.sounds = {}
        self.enabled = False
        self.current_music = None
        self.paused = False
        self._failed_music = set()

    def initialize(self):
        if self.enabled:
            return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.set_num_channels(32)
        except pygame.error as exc:
            LOGGER.warning("Áudio indisponível: %s", exc)
            return

        self.enabled = True
        self._failed_music.clear()
        for name, path in SFX.items():
            try:
                sound = pygame.mixer.Sound(str(ASSET_ROOT / path))
                sound.set_volume(self.sfx_volume)
                self.sounds[name] = sound
            except (pygame.error, OSError) as exc:
                LOGGER.warning("Não foi possível carregar %s: %s", path, exc)

    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        if self.enabled:
            pygame.mixer.music.set_volume(self.music_volume)

    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)

    def play_sfx(self, name):
        if self.enabled and not self.paused:
            sound = self.sounds.get(name)
            if sound is not None:
                # Permite golpes simultâneos sem interromper a música.
                channel = pygame.mixer.find_channel(force=True)
                if channel is not None:
                    channel.play(sound)

    def stop_sfx(self, name):
        sound = self.sounds.get(name)
        if self.enabled and sound is not None:
            sound.stop()

    def play_music(self, name):
        if not self.enabled or name == self.current_music:
            return
        pygame.mixer.music.stop()
        self.current_music = None
        if name is None or name in self._failed_music:
            return
        try:
            pygame.mixer.music.load(str(ASSET_ROOT / MUSIC[name]))
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops=-1, start=MUSIC_START.get(name, 0.0))
            self.current_music = name
        except (pygame.error, OSError) as exc:
            self._failed_music.add(name)
            LOGGER.warning("Não foi possível tocar %s: %s", name, exc)

    def update_state(self, state, level_index=None, boss_defeated=False):
        """Recebe o índice da fase (0–5); mantém a faixa entre frames/fases iguais."""
        if not self.enabled:
            return
        if state == "paused":
            if not self.paused:
                pygame.mixer.music.pause()
                pygame.mixer.pause()
                self.paused = True
            return
        if self.paused:
            pygame.mixer.music.unpause()
            pygame.mixer.unpause()
            self.paused = False

        if state in ("menu", "character_select", "controls", "credits", "settings"):
            track = "menu"
        elif state == "playing" and level_index in range(6):
            if level_index < 4:
                track = "background"
            elif boss_defeated:
                track = None  # chefe derrotado: silêncio até a próxima fase
            else:
                track = "miniboss" if level_index == 4 else "finalboss"
        else:
            track = None
        self.play_music(track)

    def shutdown(self):
        if self.enabled:
            pygame.mixer.music.stop()
            pygame.mixer.stop()
        self.sounds.clear()
        self.current_music = None
        self.paused = False
        self.enabled = False


audio = AudioManager()
