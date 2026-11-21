"""HTTP routes."""
from flask import Blueprint, current_app, jsonify, request

from .db import get_db

bp = Blueprint("api", __name__)


def _row_to_dict(row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
        "created_at": row["created_at"],
    }


def _get_task(task_id: int):
    return get_db().execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()


@bp.get("/")
def index():
    return jsonify(service="task-api", version=current_app.config["APP_VERSION"])


@bp.get("/health")
def health():
    try:
        get_db().execute("SELECT 1")
        return jsonify(status="ok")
    except Exception as exc:  # pragma: no cover
        return jsonify(status="error", detail=str(exc)), 503


@bp.get("/tasks")
def list_tasks():
    rows = get_db().execute("SELECT * FROM tasks ORDER BY id").fetchall()
    return jsonify([_row_to_dict(r) for r in rows])


@bp.post("/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    if not title:
        return jsonify(error="'title' is required"), 400
    db = get_db()
    cur = db.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
    db.commit()
    return jsonify(_row_to_dict(_get_task(cur.lastrowid))), 201


@bp.get("/tasks/<int:task_id>")
def get_task(task_id: int):
    row = _get_task(task_id)
    if row is None:
        return jsonify(error="task not found"), 404
    return jsonify(_row_to_dict(row))


@bp.patch("/tasks/<int:task_id>")
def update_task(task_id: int):
    if _get_task(task_id) is None:
        return jsonify(error="task not found"), 404
    data = request.get_json(silent=True) or {}
    db = get_db()
    if "title" in data:
        title = str(data["title"]).strip()
        if not title:
            return jsonify(error="'title' cannot be empty"), 400
        db.execute("UPDATE tasks SET title = ? WHERE id = ?", (title, task_id))
    if "done" in data:
        db.execute("UPDATE tasks SET done = ? WHERE id = ?", (int(bool(data["done"])), task_id))
    db.commit()
    return jsonify(_row_to_dict(_get_task(task_id)))


@bp.delete("/tasks/<int:task_id>")
def delete_task(task_id: int):
    db = get_db()
    cur = db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    if cur.rowcount == 0:
        return jsonify(error="task not found"), 404
    return "", 204
