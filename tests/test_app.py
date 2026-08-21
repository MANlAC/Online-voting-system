import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_homepage_loads(client):
    response = client.get("/")
    assert response.status_code == 200


def test_invalid_login_does_not_crash(client):
    response = client.post(
        "/login",
        data={"voterid": "999999", "password": "wrong"},
        follow_redirects=False,
    )
    assert response.status_code in (200, 302)
