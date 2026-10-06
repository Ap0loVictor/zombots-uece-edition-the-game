import random
import unittest
from itertools import combinations
from unittest.mock import patch

from src import main
from src.game.entities.Enemy import Enemy, FinalBoss, SubBoss
from src.game.mechanics.Physics import check_aabb_collision, get_world_hitbox


class EnemySpawningTests(unittest.TestCase):
    def setUp(self):
        # Estes testes verificam geração e colisão; os assets têm testes próprios.
        frame = object()
        loader = patch("src.game.entities.Enemy.get_enemy_animations", return_value={
            "idle": [frame], "walk": [frame], "attack": [frame],
        })
        loader.start()
        self.addCleanup(loader.stop)

    def test_regular_phases_randomize_counts_and_y_at_fixed_right_edge(self):
        expected_types = (
            {"zombie", "zombot"}, {"zombie", "robot"},
            {"zombie", "robot", "bobie"}, {"zombie", "robot"},
        )
        for phase in range(4):
            counts, layouts = set(), set()
            for seed in range(20):
                with self.subTest(phase=phase, seed=seed):
                    with patch.object(main, "random", random.Random(seed)):
                        enemies = main.spawnar_fase(phase, 800, 600)
                    counts.add(len(enemies))
                    layouts.add(tuple(enemy.y for enemy in enemies))
                    self.assertGreaterEqual(len(enemies), main.MIN_INIMIGOS_REGULARES)
                    self.assertLessEqual(len(enemies), main.MAX_INIMIGOS_REGULARES)
                    self.assertEqual({e.enemy_type for e in enemies}, expected_types[phase])
                    for enemy in enemies:
                        self.assertIs(type(enemy), Enemy)
                        self.assertEqual(enemy.x + enemy.width, phase * main.LARGURA_FASE + 800)
                        self.assertGreaterEqual(enemy.y, 0)
                        self.assertLessEqual(enemy.y + enemy.height, 600)
                        self.assertEqual(enemy.damage, 5)
                    for first, second in combinations(enemies, 2):
                        self.assertFalse(check_aabb_collision(
                            *get_world_hitbox(first), *get_world_hitbox(second)
                        ))
            self.assertGreater(len(counts), 1)
            self.assertGreater(len(layouts), 1)

    def test_top_middle_and_bottom_are_reachable(self):
        with patch.object(main.random, "randint", side_effect=[3, 0, 146, 292]):
            with patch.object(main.random, "shuffle"):
                enemies = main.fase_3(1800, 800, 600)
        self.assertEqual([enemy.y for enemy in enemies], [0, 236, 472])
        self.assertEqual(enemies[-1].y + enemies[-1].height, 600)

    def test_minimum_and_maximum_counts_can_be_spawned(self):
        for phase, minimum in enumerate((2, 2, 3, 3)):
            for choose_max in (False, True):
                with self.subTest(phase=phase, choose_max=choose_max):
                    with patch.object(main.random, "randint", side_effect=lambda a, b: b if choose_max else a):
                        enemies = main.spawnar_fase(phase, 800, 600)
                    self.assertEqual(len(enemies), 5 if choose_max else minimum)

    def test_smaller_viewport_limits_count_to_available_vertical_space(self):
        with patch.object(main.random, "randint", side_effect=lambda a, b: b):
            enemies = main.fase_3(1800, 640, 400)
        self.assertEqual(len(enemies), 4)
        for enemy in enemies:
            self.assertEqual(enemy.x + enemy.width, 2440)
            self.assertLessEqual(enemy.y + enemy.height, 400)

    def test_spawned_enemies_can_move_toward_player_without_blocking_each_other(self):
        with patch.object(main.random, "randint", side_effect=lambda a, b: b):
            enemies = main.fase_1(0, 800, 600)
        for enemy in enemies:
            previous_x = enemy.x
            enemy.update(1 / 60, target=(50, enemy.y), solid_entities=enemies, bounds=(0, 0, 5400, 600))
            self.assertLess(enemy.x, previous_x)

    def test_boss_phases_keep_exact_count_position_and_stats_without_randomness(self):
        with patch.object(main.random, "randint", side_effect=AssertionError("Boss spawn must not be random")):
            for phase, cls, health, damage, speed in (
                (4, SubBoss, 200, 25, 80), (5, FinalBoss, 500, 40, 60),
            ):
                with self.subTest(phase=phase):
                    enemies = main.spawnar_fase(phase, 800, 600)
                    self.assertEqual(len(enemies), 1)
                    boss = enemies[0]
                    self.assertIs(type(boss), cls)
                    self.assertEqual(boss.get_position(), (phase * main.LARGURA_FASE + 400, 50))
                    self.assertEqual((boss.health, boss.damage, boss.speed), (health, damage, speed))


if __name__ == "__main__":
    unittest.main()
