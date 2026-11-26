import secrets
import hmac
from flask import request, session, abort


def install_csrf(app):
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

