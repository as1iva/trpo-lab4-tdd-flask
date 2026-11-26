from flask import Flask, render_template


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(config or {})
    @app.get("/")
    def index():
        return render_template("index.html")

    return app
