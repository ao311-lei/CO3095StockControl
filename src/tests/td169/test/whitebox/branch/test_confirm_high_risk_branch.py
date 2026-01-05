import unittest

from Service.confirm_service import ConfirmService


class TestConfirmHighRiskBranch(unittest.TestCase):
    # Working input
    def test_confirm_true(self):
        service = ConfirmService(confirmer=lambda msg: True)
        self.assertTrue(service.require_confirm("confirm"))

    # Invalid (user says no)
    def test_confirm_false(self):
        service = ConfirmService(confirmer=lambda msg: False)
        with self.assertRaises(PermissionError):
            service.require_confirm("confirm")
