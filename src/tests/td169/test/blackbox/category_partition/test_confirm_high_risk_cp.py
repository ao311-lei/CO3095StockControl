import unittest

from Service.confirm_service import ConfirmService


class TestConfirmHighRiskCP(unittest.TestCase):
    def test_confirm_true_allows(self):
        s = ConfirmService(confirmer=lambda msg: True)
        s.require_confirm("CONFIRM ACTION")

    def test_confirm_false_blocks(self):
        s = ConfirmService(confirmer=lambda msg: False)
        with self.assertRaises(PermissionError):
            s.require_confirm("CONFIRM ACTION")

    def test_confirm_none_blocks(self):
        s = ConfirmService(confirmer=lambda msg: None)
        with self.assertRaises(PermissionError):
            s.require_confirm("CONFIRM ACTION")

    def test_message_passed_to_confirmer(self):
        captured = {"msg": None}

        def confirmer(msg):
            captured["msg"] = msg
            return True

        s = ConfirmService(confirmer=confirmer)
        s.require_confirm("DELETE SKU1")
        self.assertEqual(captured["msg"], "DELETE SKU1")

    def test_blank_message_allowed(self):
        s = ConfirmService(confirmer=lambda msg: True)
        s.require_confirm("")

