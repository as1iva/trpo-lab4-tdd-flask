import os
import sqlite3
from pathlib import Path
from flask import Flask, render_template, request, redirect, abort

MAX_TITLE_LENGTH = 200


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(DATABASE=str(Path(app.instance_path) / "tasks.sqlite3"))
    app.config.update(config or {})
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(app.config["DATABASE"]) as db:
        db.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0)")

    def connect():
        db = sqlite3.connect(app.config["DATABASE"])
        db.row_factory = sqlite3.Row
        return db

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
        return render_template("index.html", tasks=visible)

    return app
