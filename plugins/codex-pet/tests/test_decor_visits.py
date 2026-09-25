from test_pet import pet
from garden_motion import Gardener
import unittest

class DecorVisitTests(unittest.TestCase):
    def begin(self):
        brain=Gardener();brain.visit_wait=0;brain.elapsed=5
        decor={'nest':[590,240]};brain.advance(.1,None,decor)
        return brain,decor
    def test_nest_approach_sleep_wake_and_depart(self):
        brain,decor=self.begin();seen=[]
        for _ in range(350):
            self.assertIsNone(brain.advance(.1,None,decor))
            seen.append(brain.mode)
        self.assertIn('look',seen);self.assertIn('sleep',seen);self.assertIn('stretch',seen)
        self.assertIsNone(brain.visit)
    def test_work_interrupts_visit_without_emitting_work_early(self):
        brain,decor=self.begin();proposal={'action':'water','plot':1,'species':'clover','revision':0}
        self.assertIsNone(brain.advance(.1,proposal,decor));self.assertIsNone(brain.visit)
        for _ in range(60):brain.advance(.1,proposal,decor)
        self.assertEqual(brain.plan,proposal)
    def test_moved_or_stored_prop_cancels_visit(self):
        for decor in ({},{'nest':[600,250]}):
            brain,_=self.begin();brain.advance(.1,None,decor)
            self.assertIsNone(brain.visit);self.assertEqual(brain.mode,'rest')
