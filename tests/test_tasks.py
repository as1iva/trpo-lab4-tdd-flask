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

def test_save_edit_and_validate(client):
    client.post("/tasks", data={"title": "Старое название"})
    client.post("/tasks/1/toggle")
    response = client.post("/tasks/1/edit", data={"title": "  Новое название  "})
    assert response.status_code == 302
    html = client.get("/").text
    assert "Новое название" in html and "Старое название" not in html
    assert 'data-done="1"' in html
    for title in ["", " " , "x" * 201]:
        assert client.post("/tasks/1/edit", data={"title": title}).status_code == 400
    assert "Новое название" in client.get("/").text

def test_delete_only_selected_task(client):
    client.post("/tasks", data={"title": "Удалить эту"})
    client.post("/tasks", data={"title": "Оставить эту"})
    assert client.post("/tasks/1/delete").status_code == 302
    html = client.get("/").text
    assert "Удалить эту" not in html and "Оставить эту" in html
    assert client.get("/tasks/2/delete").status_code == 405

@pytest.mark.parametrize("method,path", [("get", "/tasks/999/edit"), ("post", "/tasks/999/edit"), ("post", "/tasks/999/toggle"), ("post", "/tasks/999/delete")])
def test_missing_task(client, method, path):
    assert getattr(client, method)(path, data={"title": "Название"}).status_code == 404

def test_status_filters(client):
    client.post("/tasks", data={"title": "Активная запись"})
    client.post("/tasks", data={"title": "Завершенная запись"})
    client.post("/tasks/2/toggle")
    active = client.get("/?status=active").text
    completed = client.get("/?status=completed").text
    assert "Активная запись" in active and "Завершенная запись" not in active
    assert "Завершенная запись" in completed and "Активная запись" not in completed
    assert "Активная запись" in client.get("/?status=all").text
    assert client.get("/?status=unknown").status_code == 400

def test_persistence_across_app_instances(tmp_path):
    from todo import create_app
    config = {"TESTING": True, "DATABASE": str(tmp_path / "persistent.sqlite3")}
    first = create_app(config).test_client()
    first.post("/tasks", data={"title": "Пережить перезапуск"})
    first.post("/tasks/1/toggle")
    second = create_app(config).test_client()
    html = second.get("/").text
    assert "Пережить перезапуск" in html
    assert 'data-done="1"' in html
