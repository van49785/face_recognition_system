# API login/logout
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.auth_service import login_admin, logout_admin
from app.models.admin import Admin
from app.db import db

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify(error="Username or password cannot be empty"), 400

    token, err = login_admin(username, password)
    if err:
        return jsonify(error=err), 401

    return jsonify(token=token, username=username), 200

@auth_bp.route("/verify", methods=["GET"])
@jwt_required()
def verify():
    admin_id = get_jwt_identity()
    admin = Admin.query.get(admin_id)
    return jsonify(valid=True, admin_id=admin.id, username=admin.username), 200

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    admin_id = get_jwt_identity()
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    logout_admin(admin_id, token)
    return jsonify(msg="Logout successfully"), 200
