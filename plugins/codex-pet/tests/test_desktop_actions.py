import unittest
from desktop_actions import growth_events

class GrowthNoticeTests(unittest.TestCase):
    def test_only_level_and_form_notices(self):
        a=dict(level=4,form='幼芽');b=dict(level=5,form='灵芽')
        self.assertEqual(growth_events(None,b),[])
        self.assertEqual(len(growth_events(a,b)),2)
        self.assertEqual(growth_events(b,b),[])
