from fastapi.testclient import TestClient
import pytest

from app import get_application


@pytest.fixture
def client():
    app = get_application()
    with TestClient(app) as client:
        yield client
