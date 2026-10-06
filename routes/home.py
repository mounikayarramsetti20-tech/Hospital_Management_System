from flask import Blueprint, render_template


home_bp = Blueprint(
    "home",
    __name__
)


# =========================================================
# HOME PAGE
# =========================================================

@home_bp.route("/")
def home():
    return render_template("home.html")


# =========================================================
# HEALTH CHECK
# =========================================================

@home_bp.route("/health")
def health():

    return {
        "status": "success",
        "message": "Hospital Management API is running"
    }


# =========================================================
# 404 ERROR
# =========================================================

@home_bp.app_errorhandler(404)
def page_not_found(error):

    return {
        "success": False,
        "message": "Page not found"
    }, 404


# =========================================================
# 500 ERROR
# =========================================================

@home_bp.app_errorhandler(500)
def internal_server_error(error):

    return {
        "success": False,
        "message": "Internal server error"
    }, 500