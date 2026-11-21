"""Task API application factory."""
import logging
import os

from flask import Flask, jsonify

from . import db
from .routes import bp


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=os.environ.get("DATABASE_PATH", "/data/tasks.db"),
        APP_VERSION=os.environ.get("APP_VERSION", "1.0.0"),
    )
    if config:
        app.config.update(config)

    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    db.init_app(app)
    app.register_blueprint(bp)

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify(error="not found"), 404

    @app.errorhandler(405)
    def method_not_allowed(_e):
        return jsonify(error="method not allowed"), 405

    return app
