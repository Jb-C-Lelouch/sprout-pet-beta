import unittest
import rules

class ProgressionTests(unittest.TestCase):
    def test_level_boundaries_and_cap(self):
        for level in range(1,31):
            threshold=5*level*(level-1)
            self.assertEqual(rules.progression_xp(threshold)['level'],level)
            if level>1:self.assertEqual(rules.progression_xp(threshold-1)['level'],level-1)
        state=rules.progression_xp(6000)
        self.assertEqual(state['level'],30)
        self.assertEqual(state['level_progress'],1650)
        self.assertIsNone(state['next_level_cost'])
