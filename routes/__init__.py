from functools import wraps

from flask import jsonify
from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt
)


def admin_required():

    def decorator(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):

            verify_jwt_in_request()

            claims = get_jwt()

            if claims.get("role") != "admin":

                return jsonify({
                    "success": False,
                    "message": "Admin access required"
                }), 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def doctor_or_admin_required():

    def decorator(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):

            verify_jwt_in_request()

            claims = get_jwt()

            role = claims.get("role")

            if role not in ["admin", "doctor"]:

                return jsonify({
                    "success": False,
                    "message": "Access denied"
                }), 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator


# =========================================================
# BLUEPRINT REGISTRATION
# =========================================================

def register_routes(app):

    from routes.auth import auth_bp
    from routes.patients import patients_bp
    from routes.doctors import doctors_bp
    from routes.appointments import appointments_bp
    from routes.treatments import treatments_bp
    from routes.data import data_bp
    from routes.home import home_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(doctors_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(treatments_bp)
    app.register_blueprint(data_bp)
    app.register_blueprint(home_bp)