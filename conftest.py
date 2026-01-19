import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
import pytest

@pytest.fixture(autouse=True)
def reset_reservation_file():
    # Import the actual module object that tests patch
    import Repo.reservation_repo as reservation_repo_module

    original = reservation_repo_module.RESERVATION_FILE
    try:
        yield
    finally:
        reservation_repo_module.RESERVATION_FILE = original
