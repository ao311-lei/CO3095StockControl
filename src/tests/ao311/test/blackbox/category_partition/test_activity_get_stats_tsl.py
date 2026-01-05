"""
CO3095 - Black-box Category Partition (TSLGenerator derived)
Target: ActivityService.get_stats(hours)
TSL spec: specs/activity_get_stats.tsl
Uses a temporary audit file to avoid touching real project data.
"""

import unittest
import tempfile
import os
from datetime import datetime, timedelta

from Service.activity_service import ActivityService


def write_audit_lines(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def fmt(ts, msg):
    return f"{ts.strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n"


class TestActivityGetStatsTSL(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.tmp.close()
        self.svc = ActivityService(filename=self.tmp.name)

    def tearDown(self):
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    def test_missing_file_returns_empty_stats(self):
        # Frame: FileState=Missing
        os.unlink(self.tmp.name)
        stats = self.svc.get_stats(hours=24)
        self.assertEqual(sum(stats["total_by_action"].values()), 0)
        self.assertEqual(sum(stats["total_by_user"].values()), 0)

    def test_empty_file(self):
        # Frame: LineContent=EmptyFile
        write_audit_lines(self.tmp.name, [])
        stats = self.svc.get_stats(hours=24)
        self.assertEqual(sum(stats["total_by_action"].values()), 0)

    def test_older_than_cutoff_only(self):
        # Frame: OlderThanCutoffOnly
        old_ts = datetime.now() - timedelta(hours=48)
        write_audit_lines(self.tmp.name, [fmt(old_ts, "USER=adora ACTION=LOGIN SUCCESS")])
        stats = self.svc.get_stats(hours=24)
        self.assertEqual(sum(stats["total_by_action"].values()), 0)

    def test_valid_recent_user_action(self):
        # Frame: ValidRecentUserAction
        recent = datetime.now() - timedelta(hours=1)
        write_audit_lines(self.tmp.name, [fmt(recent, "USER=adora ACTION=LOGIN SUCCESS")])
        stats = self.svc.get_stats(hours=24)
        self.assertEqual(stats["total_by_user"]["adora"], 1)
        self.assertEqual(stats["total_by_action"]["LOGIN"], 1)
        self.assertEqual(stats["actions_by_user"]["adora"]["LOGIN"], 1)

    def test_recent_missing_user_ignored(self):
        # Frame: RecentMissingUser
        recent = datetime.now() - timedelta(hours=1)
        write_audit_lines(self.tmp.name, [fmt(recent, "ACTION=LOGIN SUCCESS")])
        stats = self.svc.get_stats(hours=24)
        self.assertEqual(sum(stats["total_by_action"].values()), 0)

    def test_recent_missing_action_ignored(self):
        # Frame: RecentMissingAction
        recent = datetime.now() - timedelta(hours=1)
        write_audit_lines(self.tmp.name, [fmt(recent, "USER=adora SUCCESS")])
        stats = self.svc.get_stats(hours=24)
        self.assertEqual(sum(stats["total_by_action"].values()), 0)

    def test_recent_login_fail_counted(self):
        # Frame: RecentLoginFail
        recent = datetime.now() - timedelta(hours=1)
        write_audit_lines(self.tmp.name, [
            fmt(recent, "USER=adora ACTION=LOGIN FAIL reason=bad_password")
        ])
        stats = self.svc.get_stats(hours=24)
        self.assertEqual(stats["failed_logins_by_user"]["adora"], 1)

    def test_mixed_users_actions(self):
        # Frame: MixedUsersActions
        recent = datetime.now() - timedelta(hours=1)
        lines = [
            fmt(recent, "USER=adora ACTION=LOGIN SUCCESS"),
            fmt(recent, "USER=adora ACTION=ASSIGN_ROLE SUCCESS"),
            fmt(recent, "USER=bob ACTION=LOGIN FAIL reason=user_not_found"),
        ]
        write_audit_lines(self.tmp.name, lines)
        stats = self.svc.get_stats(hours=24)

        self.assertEqual(stats["total_by_user"]["adora"], 2)
        self.assertEqual(stats["total_by_user"]["bob"], 1)
        self.assertEqual(stats["total_by_action"]["LOGIN"], 2)
        self.assertEqual(stats["total_by_action"]["ASSIGN_ROLE"], 1)
        self.assertEqual(stats["failed_logins_by_user"]["bob"], 1)


if __name__ == "__main__":
    unittest.main()
