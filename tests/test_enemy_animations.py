import os
import unittest
from collections import defaultdict
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from assets.sprites.entities.EnemySprite import ENEMY_ANIMATIONS, get_enemy_sprite
from src import main
from src.engine.sprite import draw_sprite_scaled
from src.game.entities.Enemy import Enemy, FinalBoss, SubBoss
from src.game.entities.Player import Player


class EnemyAnimationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.display.init()
        pygame.display.set_mode((800, 600))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.player = Player(100, 100, invincibility_duration=0)
        self.enemy = Enemy(100, 100, enemy_type="bobie", speed=0, damage=5)

    def test_all_types_load_new_assets_and_render_frames_at_entity_size(self):
        screen = pygame.display.get_surface()
        for enemy_type, paths in ENEMY_ANIMATIONS.items():
            with self.subTest(enemy_type=enemy_type):
                with patch("pygame.image.load", wraps=pygame.image.load) as load:
                    enemy = Enemy(100, 100, enemy_type=enemy_type)
                self.assertEqual(
                    {call.args[0] for call in load.call_args_list},
                    {"assets/pxos/" + path for path, _ in paths.values()},
                )
                self.assertEqual(load.call_count, 3)
                self.assertEqual(len(enemy.walk_frames), 8)
                self.assertEqual(len(enemy.attack_frames), 8)
                for frame in [enemy.sprite_idle] + enemy.walk_frames + enemy.attack_frames:
                    self.assertEqual(frame.width / frame.height, 0.5)
                    self.assertTrue(frame.matrix[:, :, 3].any())
                    draw_sprite_scaled(screen, frame.matrix, 100, 100, enemy.height)
                expected_shape = (256, 128, 4) if enemy_type == "zombie" else (64, 32, 4)
                self.assertEqual(enemy.attack_frames[0].matrix.shape, expected_shape)
                self.assertEqual(get_enemy_sprite(enemy_type).matrix.shape, (64, 32, 4))

    def test_walk_cycles_and_returns_to_idle_when_stopped_or_blocked(self):
        for enemy_type in ENEMY_ANIMATIONS:
            with self.subTest(enemy_type=enemy_type):
                enemy = Enemy(500, 100, enemy_type=enemy_type)
                frames = set()
                for _ in range(8):
                    enemy.update(0.12, target=(0, 100))
                    frames.add(id(enemy.sprite))
                    self.assertTrue(enemy.flip_x)
                self.assertEqual(len(frames), 8)
                enemy.update(0.12)
                self.assertIs(enemy.sprite, enemy.sprite_idle)
                enemy.update(0.12, target=(1000, 100), bounds=(0, 0, enemy.x + 49, 600))
                self.assertIs(enemy.sprite, enemy.sprite_idle)

    def test_attack_requires_hitbox_overlap_not_sprite_overlap(self):
        for dx, dy in ((40, 0), (32, 0), (-32, 0), (0, 90), (0, -90)):
            with self.subTest(dx=dx, dy=dy):
                self.enemy.x, self.enemy.y = 100 + dx, 100 + dy
                self.assertFalse(self.enemy.try_attack(self.player))
                self.assertFalse(self.enemy.is_attacking)
                self.assertEqual(self.player.health, 100)
        self.enemy.x, self.enemy.y = 131, 100
        self.assertTrue(self.enemy.try_attack(self.player))
        self.assertIs(self.enemy.sprite, self.enemy.attack_frames[0])
        self.assertTrue(self.enemy.flip_x)
        self.assertEqual(self.player.health, 95)

    def test_attack_plays_all_frames_without_restarting_during_contact(self):
        for enemy_type in ENEMY_ANIMATIONS:
            with self.subTest(enemy_type=enemy_type):
                enemy = Enemy(100, 100, enemy_type=enemy_type, speed=0)
                self.assertTrue(enemy.try_attack(self.player))
                frames = {id(enemy.sprite)}
                for _ in range(7):
                    enemy.update(0.08, target=self.player.get_position())
                    frames.add(id(enemy.sprite))
                    self.assertFalse(enemy.try_attack(self.player))
                self.assertEqual(len(frames), 8)
                enemy.update(0.05)
                self.assertFalse(enemy.is_attacking)
                self.assertIs(enemy.sprite, enemy.sprite_idle)

    def test_one_damage_attempt_per_second_during_continuous_contact(self):
        with patch.object(self.player, "receive_damage", wraps=self.player.receive_damage) as damage:
            self.assertTrue(self.enemy.try_attack(self.player))
            for _ in range(3):
                self.enemy.update(0.25)
                self.assertFalse(self.enemy.try_attack(self.player))
            self.assertEqual(damage.call_count, 1)
            self.enemy.update(0.25)
            self.assertTrue(self.enemy.try_attack(self.player))
            self.assertEqual(damage.call_count, 2)
            self.assertEqual(self.player.health, 90)
            self.assertFalse(self.enemy.try_attack(self.player))

    def test_leaving_and_reentering_does_not_reset_cooldown(self):
        self.enemy.try_attack(self.player)
        self.enemy.update(0.625)
        self.player.x = 400
        self.assertFalse(self.enemy.try_attack(self.player))
        self.player.x = 100
        self.assertFalse(self.enemy.try_attack(self.player))
        self.enemy.update(0.375)
        self.player.x = 400
        self.assertFalse(self.enemy.try_attack(self.player))
        self.player.x = 100
        self.assertTrue(self.enemy.try_attack(self.player))

    def test_blocked_damage_still_starts_animation_and_consumes_cooldown(self):
        for immunity in ("invincibility_remaining", "dash_timer"):
            with self.subTest(immunity=immunity):
                player = Player(100, 100)
                setattr(player, immunity, 2.0)
                enemy = Enemy(100, 100, enemy_type="robot", damage=5)
                self.assertTrue(enemy.try_attack(player))
                self.assertTrue(enemy.is_attacking)
                self.assertEqual(player.health, 100)
                setattr(player, immunity, 0.0)
                self.assertFalse(enemy.try_attack(player))
                self.assertEqual(player.health, 100)

    def test_cooldowns_are_independent_and_dead_entities_cannot_attack(self):
        other = Enemy(100, 100, enemy_type="zombot", damage=5)
        self.assertTrue(self.enemy.try_attack(self.player))
        self.assertTrue(other.try_attack(self.player))
        self.assertEqual(self.player.health, 90)
        self.enemy.update(1.0)
        self.enemy.alive = False
        self.assertFalse(self.enemy.try_attack(self.player))
        self.enemy.alive = True
        self.player.alive = False
        self.assertFalse(self.enemy.try_attack(self.player))

    def test_attack_stops_chasing_but_preserves_knockback(self):
        self.enemy.movement.speed = 100
        self.enemy.try_attack(self.player)
        self.enemy.update(0.1, target=(400, 100))
        self.assertEqual(self.enemy.get_position(), (100, 100))
        self.enemy.apply_knockback(-100, 0)
        self.enemy.update(0.1, target=(400, 100))
        self.assertEqual(self.enemy.get_position(), (90, 100))
        self.assertTrue(self.enemy.is_attacking)

    def test_game_loop_triggers_attack_before_rendering_without_extra_damage(self):
        game = main.nova_partida(800, 600)
        game["player"] = self.player
        game["enemies"] = [self.enemy]
        game["things"] = [self.player, self.enemy]
        screen = pygame.display.get_surface()
        with patch.object(self.player, "receive_damage", wraps=self.player.receive_damage) as damage:
            with patch.object(main, "renderizeBeings") as render:
                render.side_effect = lambda *args, **kwargs: self.assertIs(
                    self.enemy.sprite, self.enemy.attack_frames[0]
                )
                main.atualizar_partida(game, screen, 0, defaultdict(bool))
            for _ in range(3):
                main.atualizar_partida(game, screen, 0.25, defaultdict(bool))
            self.assertEqual(damage.call_count, 1)
            main.atualizar_partida(game, screen, 0.25, defaultdict(bool))
            self.assertEqual(damage.call_count, 2)

    def test_bobie_spawns_in_phase_three_and_boss_stats_are_preserved(self):
        enemies = main.fase_3(1800, 800, 600)
        self.assertEqual({enemy.enemy_type for enemy in enemies}, {"zombie", "robot", "bobie"})
        for boss_type, health, damage, speed in ((SubBoss, 200, 25, 80), (FinalBoss, 500, 40, 60)):
            boss = boss_type(100, 100)
            self.assertEqual((boss.health, boss.damage, boss.speed), (health, damage, speed))
            self.assertEqual(len(boss.attack_frames), 8)


if __name__ == "__main__":
    unittest.main()
