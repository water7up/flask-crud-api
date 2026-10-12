"""Minimal CRUD REST API: Flask + SQLAlchemy (ORM) + SQLite."""
from __future__ import annotations

import os
from datetime import datetime, timezone

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException

db = SQLAlchemy()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class ValidationError(Exception):
    pass


def validate(payload, *, partial: bool) -> dict:
    """Return clean fields or raise ValidationError. partial=True for PUT (only sent fields are updated)."""
    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a JSON object.")
    unknown = set(payload) - {"name", "description"}
    if unknown:
        raise ValidationError(f"Unknown field(s): {', '.join(sorted(unknown))}.")
    out = {}
    if "name" in payload or not partial:
        name = payload.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("'name' is required and must be a non-empty string.")
        if len(name.strip()) > 120:
            raise ValidationError("'name' must be at most 120 characters.")
        out["name"] = name.strip()
    if "description" in payload:
        desc = payload["description"]
        if not isinstance(desc, str):
            raise ValidationError("'description' must be a string.")
        out["description"] = desc
    if partial and not out:
        raise ValidationError("Nothing to update: send 'name' and/or 'description'.")
    return out


def create_app(database_url: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or os.environ.get("DATABASE_URL", "sqlite:///items.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.post("/items")
    def create_item():
        data = validate(request.get_json(silent=True), partial=False)
        item = Item(**data)
        db.session.add(item)
        db.session.commit()
        return jsonify(item.to_dict()), 201

    @app.get("/items")
    def list_items():
        items = db.session.execute(db.select(Item).order_by(Item.id)).scalars().all()
        return jsonify([i.to_dict() for i in items])

    @app.get("/items/<int:item_id>")
    def get_item(item_id: int):
        return jsonify(db.get_or_404(Item, item_id, description=f"Item {item_id} not found.").to_dict())

    @app.put("/items/<int:item_id>")
    def update_item(item_id: int):
        item = db.get_or_404(Item, item_id, description=f"Item {item_id} not found.")
        for key, value in validate(request.get_json(silent=True), partial=True).items():
            setattr(item, key, value)
        db.session.commit()
        return jsonify(item.to_dict())

    @app.delete("/items/<int:item_id>")
    def delete_item(item_id: int):
        item = db.get_or_404(Item, item_id, description=f"Item {item_id} not found.")
        db.session.delete(item)
        db.session.commit()
        return "", 204

    @app.errorhandler(ValidationError)
    def on_validation_error(err):
        return jsonify(error=str(err)), 400

    @app.errorhandler(HTTPException)
    def on_http_error(err):
        return jsonify(error=err.description), err.code

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
