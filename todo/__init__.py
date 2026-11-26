from flask import Flask, render_template, request, redirect, abort


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(config or {})
    tasks = []
    next_id = 1

    @app.post("/tasks")
    def create_task():
        title = request.form.get("title", "")
        if not title.strip():
            abort(400)
        nonlocal next_id
        tasks.append({"id": next_id, "title": title.strip(), "done": False})
        next_id += 1
        return redirect("/")

    @app.get("/")
    def index():
        return render_template("index.html", tasks=tasks)

    return app
