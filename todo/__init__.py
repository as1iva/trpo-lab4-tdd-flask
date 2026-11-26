from .db import connect, init_db
from pathlib import Path
import secrets
import hmac
from flask import Flask, render_template, request, redirect, abort, session

MAX_TITLE_LENGTH = 200


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY=secrets.token_hex(32), CSRF_ENABLED=True, DATABASE=str(Path(app.instance_path) / "tasks.sqlite3"))
    app.config.update(config or {})
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    with app.app_context():
        init_db()

    @app.before_request
    def protect_forms():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_hex(32)
        if request.method == "POST" and app.config["CSRF_ENABLED"]:
            supplied = request.form.get("csrf_token", "")
            if not hmac.compare_digest(supplied, session["csrf_token"]):
                abort(400, description="Неверный CSRF токен")

    @app.context_processor
    def csrf_context():
        return {"csrf_token": session.get("csrf_token", "")}

    def validated_title():
        title = request.form.get("title", "").strip()
        if not title or len(title) > MAX_TITLE_LENGTH:
            abort(400)
        return title

    def find_task(task_id):
        with connect() as db:
            task = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if task is None:
            abort(404, description="Задача не найдена")
        return task

    @app.post("/tasks")
    def create_task():
        title = validated_title()
        with connect() as db:
            db.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        return redirect("/")

    @app.post("/tasks/<int:task_id>/toggle")
    def toggle_task(task_id):
        task = find_task(task_id)
        with connect() as db:
            db.execute("UPDATE tasks SET done = ? WHERE id = ?", (not task["done"], task_id))
        return redirect("/")

    @app.post("/tasks/<int:task_id>/edit")
    def save_task(task_id):
        find_task(task_id)
        title = validated_title()
        with connect() as db:
            db.execute("UPDATE tasks SET title = ? WHERE id = ?", (title, task_id))
        return redirect("/")

    @app.get("/tasks/<int:task_id>/edit")
    def edit_task(task_id):
        return render_template("edit.html", task=find_task(task_id))

    @app.post("/tasks/<int:task_id>/delete")
    def delete_task(task_id):
        find_task(task_id)
        with connect() as db:
            db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return redirect("/")

    @app.get("/")
    def index():
        status = request.args.get("status", "all")
        if status not in ("all", "active", "completed"):
            abort(400)
        with connect() as db:
            tasks = db.execute("SELECT * FROM tasks ORDER BY id").fetchall()
        visible = tasks
        if status != "all":
            visible = [t for t in tasks if bool(t["done"]) == (status == "completed")]
        query = request.args.get("q", "").strip()
        if query:
            visible = [t for t in visible if query.casefold() in t["title"].casefold()]
        return render_template("index.html", tasks=visible, query=query)

    return app
