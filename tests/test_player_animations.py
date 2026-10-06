import importlib
import os
import unittest
from collections import defaultdict
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import numpy as np
import pygame

from src import main
from src.game.entities.Player import PERSONAGENS, Player
from src.ui.CharacterSelect import CharacterSelect


class PlayerAnimationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.display.init()
        pygame.display.set_mode((800, 600))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_imports_do_not_load_character_actions(self):
        with patch("pygame.image.load") as load:
            importlib.reload(importlib.import_module("src.game.entities.Player"))
            importlib.reload(importlib.import_module("src.ui.CharacterSelect"))
            importlib.reload(main)
        load.assert_not_called()

    def test_selection_loads_only_previews_until_confirmation(self):
        with patch("pygame.image.load", wraps=pygame.image.load) as load:
            selection = CharacterSelect(800, 600)
            selection.open()
            for _ in range(3):
                self.assertIsNone(selection.handle_event(
                    pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
                ))
            self.assertEqual(selection.handle_event(
                pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
            ), "voltar")
            self.assertEqual(load.call_count, 3)
            self.assertTrue(all("idle" in call.args[0] for call in load.call_args_list))

            for index, character in enumerate(PERSONAGENS):
                with self.subTest(character=character):
                    selection.index = index
                    load.reset_mock()
                    chosen = selection.handle_event(
                        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
                    )
                    self.assertEqual(chosen, character)
                    load.assert_not_called()
                    game = main.nova_partida(800, 600, personagem=chosen)
                    self.assertEqual(game["player"].character, character)
                    paths = [call.args[0] for call in load.call_args_list]
                    for other, data in PERSONAGENS.items():
                        if other != character:
                            self.assertFalse(any(path.startswith(data["pasta"]) for path in paths))

    def test_player_loads_own_assets_once_and_starts_idle(self):
        for character, data in PERSONAGENS.items():
            with self.subTest(character=character):
                with patch("pygame.image.load", wraps=pygame.image.load) as load:
                    player = Player(100, 100, character=character)
                paths = [call.args[0] for call in load.call_args_list]
                self.assertTrue(all(path.startswith(data["pasta"]) for path in paths))
                self.assertEqual(len(paths), len(set(paths)))
                self.assertIs(player.sprite, player.sprite_idle)
                self.assertFalse(player.is_attacking)
                self.assertFalse(player.is_moving)
                for frame in player.walk_frames + [player.sprite_windup, player.sprite_extended, player.sprite_recoil]:
                    self.assertEqual(frame.matrix.shape, (64, 32, 4))
                    self.assertTrue(np.any(frame.matrix[:, :, 3]))

    def test_attack_phases_cooldown_and_left_facing_match_apolo(self):
        for character in PERSONAGENS:
            with self.subTest(character=character):
                player = Player(100, 100, character=character, direction="left")
                keys = defaultdict(bool)
                player.start_attack()
                player.update(0.02, keys)
                self.assertIs(player.sprite, player.sprite_windup)
                self.assertTrue(player.flip_x)
                player.update(0.08, keys)
                self.assertIs(player.sprite, player.sprite_extended)
                player.update(0.07, keys)
                self.assertIs(player.sprite, player.sprite_recoil)
                player.update(0.04, keys)
                self.assertFalse(player.is_attacking)
                self.assertIs(player.sprite, player.sprite_idle)
                player.start_attack()
                self.assertFalse(player.is_attacking)
                player.update(0.2, keys)
                player.start_attack()
                self.assertTrue(player.is_attacking)
                self.assertFalse(np.array_equal(player.sprite_windup.matrix, player.sprite_extended.matrix))
                self.assertFalse(np.array_equal(player.sprite_extended.matrix, player.sprite_recoil.matrix))

    def test_walk_cycles_moves_flips_and_resets_when_stopped(self):
        for character in PERSONAGENS:
            for key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                with self.subTest(character=character, key=key):
                    player = Player(100, 100, character=character)
                    expected_count = 2 if character == "apolo" else 8
                    self.assertEqual(len(player.walk_frames), expected_count)
                    keys = defaultdict(bool, {key: True})
                    frames = set()
                    for _ in range(expected_count):
                        player.update(0.12, keys)
                        frames.add(id(player.sprite))
                        self.assertTrue(player.is_moving)
                        self.assertEqual(player.flip_x, key == pygame.K_LEFT)
                    self.assertEqual(len(frames), expected_count)
                    self.assertNotEqual(player.get_position(), (100, 100))
                    player.update(0.01, defaultdict(bool))
                    self.assertIs(player.sprite, player.sprite_idle)
                    self.assertFalse(player.is_moving)
                    player.update(0.12, keys)
                    self.assertIs(player.sprite, player.walk_frames[1])

    def test_game_update_renders_selected_character_attacking_and_walking(self):
        screen = pygame.display.get_surface()
        for character in PERSONAGENS:
            with self.subTest(character=character):
                game = main.nova_partida(800, 600, personagem=character)
                player = game["player"]
                keys = defaultdict(bool, {pygame.K_RIGHT: True})
                main.atualizar_partida(game, screen, 0.12, keys)
                self.assertIs(player.sprite, player.walk_frames[1])
                player.start_attack()
                main.atualizar_partida(game, screen, 0.02, keys)
                self.assertIs(player.sprite, player.sprite_windup)


if __name__ == "__main__":
    unittest.main()
