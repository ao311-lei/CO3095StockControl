import unittest

from Service.confirm_service import ConfirmService


class TestConfirmHighRiskConcolic(unittest.TestCase):
    # Working input
    def test_concolic_confirm_true(self):
        service = ConfirmService(confirmer=lambda msg: True)
        self.assertTrue(service.require_confirm("confirm"))

    # Invalid input
    def test_concolic_confirm_false(self):
        service = ConfirmService(confirmer=lambda msg: False)
        with self.assertRaises(PermissionError):
            service.require_confirm("confirm")
