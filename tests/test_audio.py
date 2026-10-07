"""Execute com: python -m unittest discover -s tests -v."""

import os
import unittest
from unittest.mock import patch

os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame

from src.engine.audio import AudioManager, MUSIC, SFX, audio
from src.game.entities.Enemy import Enemy
from src.game.entities.Player import Player
from src.game.entities.Villain import Professor, MrBlack
from src.ui.CharacterSelect import CharacterSelect
from src.ui.Menu import Menu


class AudioTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.manager = AudioManager()
        self.manager.initialize()

    def tearDown(self):
        self.manager.shutdown()
        pygame.quit()

    def test_actual_assets_load_and_play(self):
        self.assertEqual(set(self.manager.sounds), set(SFX))
        for name in MUSIC:
            with self.subTest(music=name):
                self.manager.play_music(name)
                self.assertTrue(pygame.mixer.music.get_busy())
                self.assertAlmostEqual(pygame.mixer.music.get_volume(), 0.4, delta=0.01)
        for name, sound in self.manager.sounds.items():
            with self.subTest(sfx=name):
                self.assertGreater(sound.get_length(), 0)
                self.manager.play_sfx(name)
                self.assertGreater(sound.get_num_channels(), 0)

    def test_state_music_loops_without_restarting_shared_tracks(self):
        with patch.object(pygame.mixer.music, "play", wraps=pygame.mixer.music.play) as play:
            for state in ("menu", "controls", "credits", "settings", "character_select"):
                self.manager.update_state(state)
                self.assertEqual(self.manager.current_music, "menu")
            self.assertEqual(play.call_count, 1)
            for level in range(4):
                for _ in range(3):
                    self.manager.update_state("playing", level)
                self.assertEqual(self.manager.current_music, "background")
            self.assertEqual(play.call_count, 2)
            self.manager.update_state("playing", 4)
            self.assertEqual(self.manager.current_music, "miniboss")
            self.manager.update_state("playing", 5)
            self.assertEqual(self.manager.current_music, "finalboss")
            self.assertEqual(play.call_count, 4)
            for call in play.call_args_list:
                self.assertEqual(call.kwargs, {"loops": -1})
            self.manager.update_state("vitoria", 5)
            self.assertFalse(pygame.mixer.music.get_busy())
            self.manager.update_state("menu", 5)
            self.assertEqual(self.manager.current_music, "menu")
            self.manager.update_state("playing", 0)
            self.assertEqual(self.manager.current_music, "background")

    def test_pause_resumes_without_restarting_and_volumes_are_independent(self):
        self.manager.update_state("playing", 4)
        with patch.object(pygame.mixer.music, "play") as play:
            self.manager.update_state("paused", 4)
            self.assertTrue(self.manager.paused)
            self.assertFalse(pygame.mixer.music.get_busy())
            self.manager.update_state("playing", 4)
            self.assertTrue(pygame.mixer.music.get_busy())
            play.assert_not_called()
        self.manager.set_music_volume(0.2)
        self.manager.set_sfx_volume(0.7)
        self.assertAlmostEqual(pygame.mixer.music.get_volume(), 0.2, delta=0.01)
        for sound in self.manager.sounds.values():
            self.assertAlmostEqual(sound.get_volume(), 0.7, delta=0.01)
        self.manager.set_music_volume(2)
        self.manager.set_sfx_volume(-1)
        self.assertEqual(pygame.mixer.music.get_volume(), 1)
        self.assertTrue(all(sound.get_volume() == 0 for sound in self.manager.sounds.values()))

    def test_unavailable_device_does_not_break_game(self):
        manager = AudioManager()
        with patch.object(pygame.mixer, "get_init", return_value=None), \
             patch.object(pygame.mixer, "init", side_effect=pygame.error("no device")), \
             self.assertLogs("src.engine.audio", level="WARNING"):
            manager.initialize()
        self.assertFalse(manager.enabled)
        manager.update_state("menu")
        manager.play_sfx("player_death")
        manager.shutdown()

    def test_missing_asset_is_logged_and_other_sounds_still_load(self):
        manager = AudioManager()
        with patch.dict(SFX, {"missing": "missing.ogg"}), \
             self.assertLogs("src.engine.audio", level="WARNING"):
            manager.initialize()
        self.assertEqual(set(manager.sounds), set(SFX))
        with patch.dict(MUSIC, {"missing": "missing.ogg"}), \
             self.assertLogs("src.engine.audio", level="WARNING") as logs:
            manager.play_music("missing")
            manager.play_music("missing")
        self.assertEqual(len(logs.output), 1)
        manager.update_state("menu")
        self.assertEqual(manager.current_music, "menu")
        manager.shutdown()


class EventTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1, 1))
        self.addCleanup(pygame.quit)
        self.patch = patch.object(audio, "play_sfx")
        self.play = self.patch.start()
        self.addCleanup(self.patch.stop)

    def test_player_attack_and_special_only_sound_when_accepted(self):
        player = Player(0, 0)
        player.start_attack()
        player.start_attack()
        self.play.assert_called_once_with("player_punch")
        self.play.reset_mock()
        self.assertIsNone(player.start_special())
        self.play.assert_not_called()
        player.special_timer = player.special_charge_time
        self.assertIsNotNone(player.start_special())
        self.assertIsNone(player.start_special())
        self.play.assert_called_once_with("hadouken")

    def test_damage_variants_blocked_damage_and_single_death(self):
        player = Player(0, 0)
        for variant in ("player_damage_1", "player_damage_2"):
            player.invincibility_remaining = 0
            with patch("src.game.entities.Player.random.choice", return_value=variant) as choice:
                self.assertTrue(player.receive_damage(5))
                choice.assert_called_once_with(("player_damage_1", "player_damage_2"))
            self.play.assert_called_with(variant)
        self.play.reset_mock()
        self.assertFalse(player.receive_damage(5))
        player.invincibility_remaining = 0
        player.start_dash()
        self.assertFalse(player.receive_damage(5))
        player.dash_timer = 0
        self.assertFalse(player.receive_damage(0))
        self.play.assert_not_called()
        self.assertTrue(player.receive_damage(1000))
        self.assertFalse(player.receive_damage(1000))
        player.start_attack()
        player.start_special()
        self.play.assert_called_once_with("player_death")

    def test_regular_enemy_death_once_for_every_type(self):
        for kind in ("zombie", "zombot", "bobie", "robot"):
            with self.subTest(kind=kind):
                self.play.reset_mock()
                enemy = Enemy(0, 0, enemy_type=kind)
                enemy.receive_damage(1)
                self.play.assert_not_called()
                enemy.receive_damage(1000)
                enemy.receive_damage(1000)
                self.play.assert_called_once_with("enemy_death")

    def test_boss_attack_special_and_death_use_own_sounds(self):
        for cls, name in ((Professor, "professor"), (MrBlack, "mrblack")):
            with self.subTest(boss=name):
                boss = cls(0, 0)
                for kind in ("punch", "kick", "special"):
                    self.play.reset_mock()
                    boss._iniciar_golpe(kind, 20)
                    boss.update(0.01)
                    effect = "special" if kind == "special" else "attack"
                    self.play.assert_called_once_with(f"{name}_{effect}")
                self.play.reset_mock()
                boss.receive_damage(1000)
                boss.receive_damage(1000)
                boss.update(0.01)
                self.play.assert_called_once_with(f"{name}_death")

    def test_navigation_sounds_only_on_changed_selection(self):
        for screen, keys in ((Menu(800, 600), (pygame.K_UP, pygame.K_DOWN)),
                             (CharacterSelect(800, 600), (pygame.K_LEFT, pygame.K_RIGHT))):
            self.play.reset_mock()
            for key in keys:
                screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key))
            self.assertEqual(self.play.call_count, 2)
            self.play.assert_called_with("menu_navigation")
            self.play.reset_mock()
            screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
            screen.handle_event(pygame.event.Event(pygame.KEYUP, key=keys[0]))
            self.play.assert_not_called()


if __name__ == "__main__":
    unittest.main()
