import os
import tempfile
import unittest
from datetime import datetime, timedelta

from Service.activity_service import ActivityService


class TestActivityServiceStatement(unittest.TestCase):


    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.tmp.close()
        self.svc = ActivityService(filename=self.tmp.name)

    def tearDown(self):
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    def test_get_stats_statement(self):
        now = datetime.now()
        within = now.strftime("%Y-%m-%d %H:%M:%S")
        old = (now - timedelta(hours=1000)).strftime("%Y-%m-%d %H:%M:%S")

        with open(self.tmp.name, "w", encoding="utf-8") as f:
            f.write("\n".join([
                "",  # skip empty
                "bad line",  # parse fail
                f"{old} - USER=a ACTION=LOGIN SUCCESS",  # filtered by cutoff
                f"{within} - USER=a ACTION=LOGIN FAIL reason=bad_password",  # counted
                f"{within} - USER=a ACTION=LOGOUT SUCCESS",  # counted
            ]) + "\n")

        stats = self.svc.get_stats(hours=24)
        self.assertEqual(stats["total_by_user"]["a"], 2)
        self.assertEqual(stats["failed_logins_by_user"]["a"], 1)
