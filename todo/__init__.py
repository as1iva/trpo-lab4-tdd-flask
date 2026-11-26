from flask import Flask, render_template, request, redirect


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(config or {})
    tasks = []

    @app.post("/tasks")
    def create_task():
        tasks.append({"id": len(tasks) + 1, "title": request.form["title"], "done": False})
        return redirect("/")

    @app.get("/")
    def index():
        return render_template("index.html", tasks=tasks)

    return app
