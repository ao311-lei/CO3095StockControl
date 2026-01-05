import unittest
from Service.confirm_service import ConfirmService


class TestConfirmHighRiskStatement(unittest.TestCase):

    # Confirm returns True
    def test_confirm_yes(self):
        svc = ConfirmService(confirmer=lambda _: True)
        self.assertTrue(svc.require_confirm("Confirm?"))

    # Confirm returns False
    def test_confirm_no(self):
        svc = ConfirmService(confirmer=lambda _: False)
        with self.assertRaises(PermissionError):
            svc.require_confirm("Confirm?")
