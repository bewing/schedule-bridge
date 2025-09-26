from fastapi.testclient import TestClient
import pytest

from schedule_bridge import app


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client
