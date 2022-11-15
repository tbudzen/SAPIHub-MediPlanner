from unittest import TestCase

from recommendation.classifiers.hypertension.HypertensionClass import HypertensionClass


class TestHypertensionClass(TestCase):

    def test_determine_class(self):
        t = HypertensionClass()
        self.assertEqual(-2, t.determineClass(90, 70))
        self.assertEqual(-2, t.determineClass(119, 79))
        self.assertEqual(-1, t.determineClass(120, 79))
        self.assertEqual(-1, t.determineClass(129, 79))
        self.assertEqual(0, t.determineClass(130, 79))
        self.assertEqual(0, t.determineClass(139, 79))
        self.assertEqual(1, t.determineClass(140, 79))
        self.assertEqual(1, t.determineClass(159, 79))
        self.assertEqual(2, t.determineClass(160, 79))
        self.assertEqual(2, t.determineClass(179, 79))
        self.assertEqual(3, t.determineClass(180, 79))
        self.assertEqual(3, t.determineClass(320, 79))

        self.assertEqual(-2, t.determineClass(90, 70))
        self.assertEqual(-2, t.determineClass(90, 79))
        self.assertEqual(-1, t.determineClass(90, 80))
        self.assertEqual(-1, t.determineClass(90, 84))
        self.assertEqual(0, t.determineClass(90, 85))
        self.assertEqual(0, t.determineClass(90, 89))
        self.assertEqual(1, t.determineClass(90, 90))
        self.assertEqual(1, t.determineClass(90, 99))
        self.assertEqual(2, t.determineClass(90, 100))
        self.assertEqual(2, t.determineClass(90, 109))
        self.assertEqual(3, t.determineClass(90, 110))
        self.assertEqual(3, t.determineClass(90, 220))

    def test_isIsolatedSystolic(self):
        t = HypertensionClass()
        self.assertEqual(True, t.isIsolatedSystolic(141, 80))
