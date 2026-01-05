"""
CO3095 - White-box (Symbolic Execution)

Unit: Service.activity_service.ActivityService
Technique: Symbolic Execution (hit parse success/fail branches and filtering)
We use a temp audit file to avoid touching real src/data/audit_log.txt.
"""

from datetime import datetime, timedelta
import os
import tempfile

from Service.activity_service import ActivityService


def test_parse_line_success_and_fail_paths():
    svc = ActivityService(filename="does_not_matter")

    ts = "2025-01-01 10:00:00 - USER=a ACTION=LOGIN SUCCESS"
    t, msg = svc._parse_line(ts)
    assert t is not None
    assert "USER=a" in msg

    bad = "not a valid line"
    t2, msg2 = svc._parse_line(bad)
    assert t2 is None
    assert msg2 is None


def test_get_stats_paths_file_missing():
    svc = ActivityService(filename="definitely_missing_12345.txt")
    stats = svc.get_stats(hours=24)
    assert sum(stats["total_by_action"].values()) == 0


def test_get_stats_paths_filters_and_counts():
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
        fname = tmp.name

        now = datetime.now()
        recent = now.strftime("%Y-%m-%d %H:%M:%S")
        old = (now - timedelta(hours=100)).strftime("%Y-%m-%d %H:%M:%S")

        tmp.write(f"{recent} - USER=u1 ACTION=LOGIN FAIL reason=bad_password\n")
        tmp.write(f"{recent} - USER=u1 ACTION=LOGIN SUCCESS\n")
        tmp.write(f"{recent} - USER=u2 ACTION=ASSIGN_ROLE target=x role=MANAGER\n")
        tmp.write(f"{old} - USER=u9 ACTION=LOGIN SUCCESS\n")  # should be filtered out

    try:
        svc = ActivityService(filename=fname)
        stats = svc.get_stats(hours=24)

        assert stats["total_by_user"]["u1"] == 2
        assert stats["total_by_user"]["u2"] == 1

        assert stats["total_by_action"]["LOGIN"] == 2
        assert stats["total_by_action"]["ASSIGN_ROLE"] == 1

        assert stats["failed_logins_by_user"]["u1"] == 1
    finally:
        if os.path.exists(fname):
            os.unlink(fname)
