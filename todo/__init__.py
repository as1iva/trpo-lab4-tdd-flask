from flask import Flask, render_template, request, redirect, abort


MAX_TITLE_LENGTH = 200

def create_app(config=None):
    app = Flask(__name__)
    app.config.update(config or {})
    tasks = []
    next_id = 1

    def validated_title():
        title = request.form.get("title", "").strip()
        if not title or len(title) > MAX_TITLE_LENGTH:
            abort(400)
        return title

    @app.post("/tasks")
    def create_task():
        title = validated_title()
        nonlocal next_id
        tasks.append({"id": next_id, "title": title, "done": False})
        next_id += 1
        return redirect("/")

    def find_task(task_id):
        task = next((t for t in tasks if t["id"] == task_id), None)
        if task is None:
            abort(404, description="Задача не найдена")
        return task

    @app.post("/tasks/<int:task_id>/toggle")
    def toggle_task(task_id):
        task = find_task(task_id)
        task["done"] = not task["done"]
        return redirect("/")

    @app.post("/tasks/<int:task_id>/edit")
    def save_task(task_id):
        task = find_task(task_id)
        task["title"] = validated_title()
        return redirect("/")

    @app.get("/tasks/<int:task_id>/edit")
    def edit_task(task_id):
        return render_template("edit.html", task=find_task(task_id))

    @app.post("/tasks/<int:task_id>/delete")
    def delete_task(task_id):
        tasks.remove(find_task(task_id))
        return redirect("/")

    @app.get("/")
    def index():
        status = request.args.get("status", "all")
        if status not in ("all", "active", "completed"):
            abort(400)
        visible = tasks
        if status != "all":
            visible = [t for t in tasks if t["done"] == (status == "completed")]
        return render_template("index.html", tasks=visible)

    return app
