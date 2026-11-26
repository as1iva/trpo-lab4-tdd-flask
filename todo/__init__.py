from flask import Flask, render_template, request, redirect, abort


MAX_TITLE_LENGTH = 200

def create_app(config=None):
    app = Flask(__name__)
    app.config.update(config or {})
    tasks = []
    next_id = 1

    @app.post("/tasks")
    def create_task():
        title = request.form.get("title", "").strip()
        if not title or len(title) > MAX_TITLE_LENGTH:
            abort(400)
        nonlocal next_id
        tasks.append({"id": next_id, "title": title, "done": False})
        next_id += 1
        return redirect("/")

    @app.get("/")
    def index():
        return render_template("index.html", tasks=tasks)

    return app
