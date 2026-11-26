import re
import sqlite3
import pytest
from todo import create_app


def test_html_escapes_user_input(client):
    title = '<script>alert("xss")</script>'
    client.post("/tasks", data={"title": title})
    html = client.get("/").text
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "&lt;script&gt;" in client.get("/tasks/1/edit").text


def test_sql_payload_is_stored_as_text(client):
    title = "'); DROP TABLE tasks; --"
    client.post("/tasks", data={"title": title})
    client.post("/tasks", data={"title": "Таблица существует"})
    assert "Таблица существует" in client.get("/").text


def test_identifier_is_not_reused(client):
    client.post("/tasks", data={"title": "Первая"})
    client.post("/tasks/1/delete")
    client.post("/tasks", data={"title": "Вторая"})
    assert 'data-id="2"' in client.get("/").text


def test_search_is_case_insensitive(client):
    client.post("/tasks", data={"title": "КУПИТЬ хлеб"})
    assert "КУПИТЬ хлеб" in client.get("/", query_string={"q": "купить"}).text


def test_search_and_filter_preserved_in_controls(client):
    html = client.get("/", query_string={"q": "книга", "status": "active"}).text
    assert 'name="status" value="active"' in html
    assert 'name="q" value="книга"' in html
    assert 'aria-current="page"' in html


def test_missing_title_field(client):
    assert client.post("/tasks", data={}).status_code == 400
    assert "Задач пока нет" in client.get("/").text


def test_separate_databases_are_isolated(tmp_path):
    first = create_app({"TESTING": True, "CSRF_ENABLED": False, "DATABASE": str(tmp_path / "a.sqlite3")}).test_client()
    second = create_app({"TESTING": True, "CSRF_ENABLED": False, "DATABASE": str(tmp_path / "b.sqlite3")}).test_client()
    first.post("/tasks", data={"title": "Только в первой"})
    assert "Только в первой" not in second.get("/").text


@pytest.mark.parametrize("token", ["", "wrong", "токен"])
def test_invalid_csrf_rejected_without_mutation(tmp_path, token):
    app = create_app({"TESTING": True, "SECRET_KEY": "test-key", "DATABASE": str(tmp_path / "csrf.sqlite3")})
    browser = app.test_client()
    assert browser.post("/tasks", data={"title": "Запрещенная запись", "csrf_token": token}).status_code == 400
    assert "Запрещенная запись" not in browser.get("/").text


def test_csrf_is_bound_to_session(tmp_path):
    app = create_app({"TESTING": True, "SECRET_KEY": "test-key", "DATABASE": str(tmp_path / "csrf.sqlite3")})
    a, b = app.test_client(), app.test_client()
    token = re.search(r'name="csrf_token" value="([^"]+)"', a.get("/").text).group(1)
    assert b.post("/tasks", data={"title": "Чужая сессия", "csrf_token": token}).status_code == 400


def test_csrf_valid_for_full_lifecycle(tmp_path):
    app = create_app({"TESTING": True, "SECRET_KEY": "test-key", "DATABASE": str(tmp_path / "csrf.sqlite3")})
    browser = app.test_client()
    token = re.search(r'name="csrf_token" value="([^"]+)"', browser.get("/").text).group(1)
    assert browser.post("/tasks", data={"title": "Создать", "csrf_token": token}).status_code == 302
    assert browser.post("/tasks/1/edit", data={"title": "Изменить", "csrf_token": token}).status_code == 302
    assert browser.post("/tasks/1/toggle", data={"csrf_token": token}).status_code == 302
    assert browser.post("/tasks/1/delete", data={"csrf_token": token}).status_code == 302
    assert "Задач пока нет" in browser.get("/").text
