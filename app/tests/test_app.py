import os
import pytest

# Ensure app module is importable
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture
def client():
    """Create test client with default env (feature flag OFF)."""
    os.environ.pop("FEATURE_NEW_GREETING", None)
    # Re-import to apply env state
    import importlib
    import app as app_module
    importlib.reload(app_module)
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c


@pytest.fixture
def client_feature_on():
    """Create test client with FEATURE_NEW_GREETING=true."""
    os.environ["FEATURE_NEW_GREETING"] = "true"
    import importlib
    import app as app_module
    importlib.reload(app_module)
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c
    os.environ.pop("FEATURE_NEW_GREETING", None)


# --- Test 1: GET / ---
def test_index_returns_json(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "service" in data
    assert "version" in data
    assert "hostname" in data


def test_index_service_name(client):
    data = client.get("/").get_json()
    assert data["service"] == "devops-cicd-lab"


# --- Test 2: GET /health ---
def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


# --- Test 3: Feature flag OFF ---
def test_greeting_flag_off(client):
    resp = client.get("/greeting")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["message"] == "Hello, World!"


# --- Test 4: Feature flag ON ---
def test_greeting_flag_on(client_feature_on):
    resp = client_feature_on.get("/greeting")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "shiny new greeting" in data["message"]
