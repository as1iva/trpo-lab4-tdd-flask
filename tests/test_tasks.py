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

def test_title_length_boundary(client):
    assert client.post("/tasks", data={"title": "я" * 201}).status_code == 400
    assert "Задач пока нет" in client.get("/").text
    assert client.post("/tasks", data={"title": "я" * 200}).status_code == 302
    assert "я" * 200 in client.get("/").text

def test_complete_task(client):
    client.post("/tasks", data={"title": "Сдать работу"})
    assert 'data-done="0"' in client.get("/").text
    assert client.post("/tasks/1/toggle").status_code == 302
    assert 'data-done="1"' in client.get("/").text

def test_reopen_task(client):
    client.post("/tasks", data={"title": "Повторить материал"})
    client.post("/tasks/1/toggle")
    client.post("/tasks/1/toggle")
    assert 'data-done="0"' in client.get("/").text

def test_edit_form(client):
    client.post("/tasks", data={"title": "Старое название"})
    response = client.get("/tasks/1/edit")
    assert response.status_code == 200
    assert 'value="Старое название"' in response.text
    assert 'action="/tasks/1/edit"' in response.text
