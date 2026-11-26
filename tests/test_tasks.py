import pytest


def test_home_is_empty(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Задач пока нет" in response.text

def test_create_task(client):
    response = client.post("/tasks", data={"title": "Изучить TDD"})
    assert response.status_code == 302
    assert response.headers["Location"] == "/"
    assert "Изучить TDD" in client.get("/").text
