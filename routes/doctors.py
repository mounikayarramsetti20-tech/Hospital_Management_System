from flask import Blueprint, request, jsonify, render_template

from models import db
from models.doctor import Doctor

from routes import admin_required


doctors_bp = Blueprint(
    "doctors",
    __name__
)


# =====================================================
# WEB PAGES
# =====================================================

@doctors_bp.route("/doctors", methods=["GET"])
def doctor_list():

    doctors = Doctor.query.order_by(
        Doctor.id.desc()
    ).all()

    return render_template(
        "doctors/list.html",
        doctors=doctors
    )


@doctors_bp.route("/doctors/new", methods=["GET"])
def doctor_new():

    return render_template(
        "doctors/form.html",
        doctor=None
    )


@doctors_bp.route("/doctors/<int:id>", methods=["GET"])
def doctor_view(id):

    doctor = db.session.get(
        Doctor,
        id
    )

    if not doctor:
        return "Doctor not found", 404

    return render_template(
        "doctors/view.html",
        doctor=doctor
    )


@doctors_bp.route("/doctors/<int:id>/edit", methods=["GET"])
def doctor_edit(id):

    doctor = db.session.get(
        Doctor,
        id
    )

    if not doctor:
        return "Doctor not found", 404

    return render_template(
        "doctors/form.html",
        doctor=doctor
    )


# =====================================================
# GET ALL DOCTORS API
# =====================================================

@doctors_bp.route(
    "/api/doctors",
    methods=["GET"]
)
def api_doctors():

    doctors = Doctor.query.order_by(
        Doctor.id.desc()
    ).all()

    return jsonify([
        doctor.to_dict()
        for doctor in doctors
    ])


# =====================================================
# GET SINGLE DOCTOR API
# =====================================================

@doctors_bp.route(
    "/api/doctors/<int:id>",
    methods=["GET"]
)
def api_get_doctor(id):

    doctor = db.session.get(
        Doctor,
        id
    )

    if not doctor:

        return jsonify({
            "success": False,
            "message": "Doctor not found"
        }), 404

    return jsonify(
        doctor.to_dict()
    )


# =====================================================
# CREATE DOCTOR API
# =====================================================

@doctors_bp.route(
    "/api/doctors",
    methods=["POST"]
)
@admin_required()
def api_create_doctor():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "JSON data is required"
        }), 400

    required_fields = [
        "name",
        "specialization",
        "contact",
        "email"
    ]

    for field in required_fields:

        if field not in data:

            return jsonify({
                "success": False,
                "message": f"{field} is required"
            }), 400

    # Check duplicate contact
    existing_contact = Doctor.query.filter_by(
        contact=data["contact"]
    ).first()

    if existing_contact:

        return jsonify({
            "success": False,
            "message": "Contact number already exists"
        }), 409

    # Check duplicate email
    existing_email = Doctor.query.filter_by(
        email=data["email"]
    ).first()

    if existing_email:

        return jsonify({
            "success": False,
            "message": "Email already exists"
        }), 409

    doctor = Doctor(
        name=data["name"],
        specialization=data["specialization"],
        contact=data["contact"],
        email=data["email"]
    )

    db.session.add(doctor)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Doctor created successfully",
        "doctor": doctor.to_dict()
    }), 201


# =====================================================
# UPDATE DOCTOR API - PUT
# =====================================================

@doctors_bp.route(
    "/api/doctors/<int:id>",
    methods=["PUT"]
)
@admin_required()
def api_put_doctor(id):

    doctor = db.session.get(
        Doctor,
        id
    )

    if not doctor:

        return jsonify({
            "success": False,
            "message": "Doctor not found"
        }), 404

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "JSON data is required"
        }), 400

    required_fields = [
        "name",
        "specialization",
        "contact",
        "email"
    ]

    for field in required_fields:

        if field not in data:

            return jsonify({
                "success": False,
                "message": f"{field} is required"
            }), 400

    # Check contact belongs to another doctor
    existing_contact = Doctor.query.filter(
        Doctor.contact == data["contact"],
        Doctor.id != id
    ).first()

    if existing_contact:

        return jsonify({
            "success": False,
            "message": "Contact number already exists"
        }), 409

    # Check email belongs to another doctor
    existing_email = Doctor.query.filter(
        Doctor.email == data["email"],
        Doctor.id != id
    ).first()

    if existing_email:

        return jsonify({
            "success": False,
            "message": "Email already exists"
        }), 409

    doctor.name = data["name"]
    doctor.specialization = data["specialization"]
    doctor.contact = data["contact"]
    doctor.email = data["email"]

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Doctor updated successfully",
        "doctor": doctor.to_dict()
    })


# =====================================================
# UPDATE DOCTOR API - PATCH
# =====================================================

@doctors_bp.route(
    "/api/doctors/<int:id>",
    methods=["PATCH"]
)
@admin_required()
def api_patch_doctor(id):

    doctor = db.session.get(
        Doctor,
        id
    )

    if not doctor:

        return jsonify({
            "success": False,
            "message": "Doctor not found"
        }), 404

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "JSON data is required"
        }), 400

    if "name" in data:
        doctor.name = data["name"]

    if "specialization" in data:
        doctor.specialization = data["specialization"]

    if "contact" in data:

        existing_contact = Doctor.query.filter(
            Doctor.contact == data["contact"],
            Doctor.id != id
        ).first()

        if existing_contact:

            return jsonify({
                "success": False,
                "message": "Contact number already exists"
            }), 409

        doctor.contact = data["contact"]

    if "email" in data:

        existing_email = Doctor.query.filter(
            Doctor.email == data["email"],
            Doctor.id != id
        ).first()

        if existing_email:

            return jsonify({
                "success": False,
                "message": "Email already exists"
            }), 409

        doctor.email = data["email"]

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Doctor updated successfully",
        "doctor": doctor.to_dict()
    })


# =====================================================
# DELETE DOCTOR API
# =====================================================

@doctors_bp.route(
    "/api/doctors/<int:id>",
    methods=["DELETE"]
)
@admin_required()
def api_delete_doctor(id):

    doctor = db.session.get(
        Doctor,
        id
    )

    if not doctor:

        return jsonify({
            "success": False,
            "message": "Doctor not found"
        }), 404

    db.session.delete(doctor)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Doctor deleted successfully"
    })