import os
import tempfile
import unittest
from datetime import datetime, timedelta

from Service.activity_service import ActivityService


class TestActivityServiceBranch(unittest.TestCase):
    """
    CO3095 White-box Branch Testing (Lecture 9 / Lab 9)

    Branches covered in get_stats():
    - FileNotFoundError path -> returns empty counters
    - Skip empty line
    - _parse_line fails -> skip
    - timestamp older than cutoff -> skip
    - missing USER/ACTION -> skip
    - LOGIN FAIL increments failed_logins_by_user
    """

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.tmp.close()
        self.svc = ActivityService(filename=self.tmp.name)

    def tearDown(self):
        # Safe cleanup even if a test deletes the file
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    def _write(self, lines):
        with open(self.tmp.name, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + ("\n" if lines else ""))

    def test_file_missing(self):
        # Delete file to force FileNotFoundError branch
        os.unlink(self.tmp.name)

        stats = self.svc.get_stats(hours=24)

        self.assertEqual(sum(stats["total_by_action"].values()), 0)
        self.assertEqual(sum(stats["total_by_user"].values()), 0)
        self.assertEqual(sum(stats["failed_logins_by_user"].values()), 0)

    def test_branches_in_parsing_and_filters(self):
        now = datetime.now()
        within = now.strftime("%Y-%m-%d %H:%M:%S")
        old = (now - timedelta(hours=1000)).strftime("%Y-%m-%d %H:%M:%S")

        self._write([
            "",  # empty line -> skip
            "not a valid line",  # parse fail -> skip
            f"{old} - USER=a ACTION=LOGIN SUCCESS",  # older than cutoff -> skip
            f"{within} - USER=a ACTION=LOGIN FAIL reason=bad_password",  # counts + failed login
            f"{within} - USER=a ACTION=LOGOUT SUCCESS",  # counts
            f"{within} - ACTION=LOGIN FAIL",  # missing USER -> skip
            f"{within} - USER=b SOMETHING=ELSE",  # missing ACTION -> skip
        ])

        stats = self.svc.get_stats(hours=24)

        self.assertEqual(stats["total_by_user"]["a"], 2)
        self.assertEqual(stats["total_by_action"]["LOGIN"], 1)
        self.assertEqual(stats["total_by_action"]["LOGOUT"], 1)
        self.assertEqual(stats["failed_logins_by_user"]["a"], 1)


if __name__ == "__main__":
    unittest.main()
