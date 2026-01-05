import random
import unittest

from Service.confirm_service import ConfirmService


class TestConfirmHighRiskRandom(unittest.TestCase):
    def setUp(self):
        random.seed(123)

    def test_random_confirm_true_allows(self):
        service = ConfirmService(confirmer=lambda prompt: True)
        for i in range(10):
            with self.subTest(i=i):
                self.assertTrue(service.require_confirm(f"Action {i}"))

    def test_random_confirm_false_blocks(self):
        service = ConfirmService(confirmer=lambda prompt: False)
        for i in range(10):
            with self.subTest(i=i):
                with self.assertRaises(PermissionError):
                    service.require_confirm(f"Action {i}")

    def test_random_mixed_confirm(self):
        def confirmer(_prompt):
            return random.choice([True, False])

        service = ConfirmService(confirmer=confirmer)

        seen_true = False
        seen_false = False

        for i in range(30):
            try:
                ok = service.require_confirm(f"Action {i}")
                self.assertTrue(ok)
                seen_true = True
            except PermissionError:
                seen_false = True

        self.assertTrue(seen_true)
        self.assertTrue(seen_false)

    def test_missing_confirmer_raises(self):
        with self.assertRaises(ValueError):
            ConfirmService(confirmer=None)
