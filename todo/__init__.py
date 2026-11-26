from flask import Flask


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(config or {})
    @app.get("/")
    def index():
        return "<h1>Мои задачи</h1><p>Задач пока нет</p>"

    return app
