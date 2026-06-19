def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "financial-intelligence-platform"


def test_health_db(client):
    response = client.get("/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["component"] == "postgresql"


def test_health_qdrant(client):
    response = client.get("/health/qdrant")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["component"] == "qdrant"
    assert data["collection_valid"] is True


def test_health_metrics(client):
    response = client.get("/health/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "qdrant" in data
    assert data["qdrant"]["collection"] == "financial_chunks"


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert data["service"] == "financial-intelligence-platform"
