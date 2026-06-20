from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_app_route_serves_frontend():
    response = client.get("/app")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Financial Intelligence Platform" in response.text


def test_static_css_is_served():
    response = client.get("/static/css/style.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]


def test_static_js_is_served():
    response = client.get("/static/js/app.js")
    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]
