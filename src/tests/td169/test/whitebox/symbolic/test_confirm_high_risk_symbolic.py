import unittest

from Service.confirm_service import ConfirmService


class TestConfirmHighRiskSymbolic(unittest.TestCase):
    # Working input where confirmer returns True)
    def test_path_confirm_true(self):
        svc = ConfirmService(confirmer=lambda _: True)
        self.assertTrue(svc.require_confirm("confirm"))

    # Invalid input
    def test_path_confirm_false(self):
        svc = ConfirmService(confirmer=lambda _: False)
        with self.assertRaises(PermissionError):
            svc.require_confirm("confirm")
