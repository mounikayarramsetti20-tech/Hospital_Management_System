from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    verify_jwt_in_request
)
from models import db
from models.user import User
from models.doctor import Doctor


auth_bp = Blueprint("auth", __name__)


# =========================================================
# LOGIN PAGE
# =========================================================

@auth_bp.route("/login", methods=["GET"])
def login_page():

    return render_template("login.html")


# =========================================================
# LOGIN API
# =========================================================

@auth_bp.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "JSON data is required"
        }), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({
            "success": False,
            "message": "Username and password are required"
        }), 400

    user = User.query.filter_by(
        username=username
    ).first()

    if not user:

        return jsonify({
            "success": False,
            "message": "Invalid username or password"
        }), 401

    if not user.check_password(password):

        return jsonify({
            "success": False,
            "message": "Invalid username or password"
        }), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role,
            "doctor_id": user.doctor_id
        }
    )

    return jsonify({
        "success": True,
        "message": "Login successful",
        "access_token": access_token,
        "user": user.to_dict()
    })


# =========================================================
# CURRENT USER
# =========================================================

@auth_bp.route("/api/me", methods=["GET"])
def current_user():

    try:

        verify_jwt_in_request()

        claims = get_jwt()

        user_id = claims.get("sub")

        user = db.session.get(
            User,
            int(user_id)
        )

        if not user:

            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        return jsonify({
            "success": True,
            "user": user.to_dict()
        })

    except Exception:

        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401