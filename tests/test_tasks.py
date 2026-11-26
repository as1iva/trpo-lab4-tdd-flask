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

@pytest.mark.parametrize("title", ["", "   "])
def test_reject_empty_title(client, title):
    response = client.post("/tasks", data={"title": title})
    assert response.status_code == 400
    assert "Задач пока нет" in client.get("/").text

def test_trim_title(client):
    client.post("/tasks", data={"title": "  Прочитать книгу  "})
    html = client.get("/").text
    assert ">Прочитать книгу</span>" in html
    assert "  Прочитать книгу  " not in html
