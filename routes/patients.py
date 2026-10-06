from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import verify_jwt_in_request

from models import db
from models.patient import Patient

from routes import admin_required


# =========================================================
# PATIENT BLUEPRINT
# =========================================================

patients_bp = Blueprint(
    "patients",
    __name__
)


# =========================================================
# WEB ROUTES
# =========================================================

# ---------------------------------------------------------
# GET /patients
# Display all patients
# ---------------------------------------------------------

@patients_bp.route(
    "/patients",
    methods=["GET"]
)
def patient_list():

    patients = Patient.query.order_by(
        Patient.id.desc()
    ).all()

    return render_template(
        "patients/list.html",
        patients=patients
    )


# ---------------------------------------------------------
# GET /patients/new
# Display add patient form
# ---------------------------------------------------------

@patients_bp.route(
    "/patients/new",
    methods=["GET"]
)
def patient_new():

    return render_template(
        "patients/form.html",
        patient=None
    )


# ---------------------------------------------------------
# GET /patients/<id>
# Display patient details
# ---------------------------------------------------------

@patients_bp.route(
    "/patients/<int:id>",
    methods=["GET"]
)
def patient_view(id):

    patient = db.session.get(
        Patient,
        id
    )

    if not patient:

        return "Patient not found", 404

    return render_template(
        "patients/view.html",
        patient=patient
    )


# ---------------------------------------------------------
# GET /patients/<id>/edit
# Display edit form
# ---------------------------------------------------------

@patients_bp.route(
    "/patients/<int:id>/edit",
    methods=["GET"]
)
def patient_edit(id):

    patient = db.session.get(
        Patient,
        id
    )

    if not patient:

        return "Patient not found", 404

    return render_template(
        "patients/form.html",
        patient=patient
    )


# =========================================================
# API ROUTES
# =========================================================

# ---------------------------------------------------------
# GET /api/patients
# Get all patients
# ---------------------------------------------------------

@patients_bp.route(
    "/api/patients",
    methods=["GET"]
)
def api_patients():

    patients = Patient.query.order_by(
        Patient.id.desc()
    ).all()

    return jsonify([
        patient.to_dict()
        for patient in patients
    ])


# ---------------------------------------------------------
# GET /api/patients/<id>
# Get one patient
# ---------------------------------------------------------

@patients_bp.route(
    "/api/patients/<int:id>",
    methods=["GET"]
)
def api_get_patient(id):

    patient = db.session.get(
        Patient,
        id
    )

    if not patient:

        return jsonify({
            "success": False,
            "message": "Patient not found"
        }), 404

    return jsonify(
        patient.to_dict()
    )


# ---------------------------------------------------------
# POST /api/patients
# Create patient
# Admin only
# ---------------------------------------------------------

@patients_bp.route(
    "/api/patients",
    methods=["POST"]
)
@admin_required()
def api_create_patient():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "JSON data is required"
        }), 400


    required_fields = [
        "name",
        "age",
        "gender",
        "contact"
    ]


    for field in required_fields:

        if field not in data:

            return jsonify({
                "success": False,
                "message": f"{field} is required"
            }), 400


    # Check duplicate contact

    existing_patient = Patient.query.filter_by(
        contact=data["contact"]
    ).first()


    if existing_patient:

        return jsonify({
            "success": False,
            "message": "Contact number already exists"
        }), 409


    # Create patient

    patient = Patient(
        name=data["name"],
        age=data["age"],
        gender=data["gender"],
        contact=data["contact"]
    )


    db.session.add(patient)

    db.session.commit()


    return jsonify({
        "success": True,
        "message": "Patient created successfully",
        "patient": patient.to_dict()
    }), 201


# ---------------------------------------------------------
# PUT /api/patients/<id>
# Full update
# ---------------------------------------------------------

@patients_bp.route(
    "/api/patients/<int:id>",
    methods=["PUT"]
)
@admin_required()
def api_put_patient(id):

    patient = db.session.get(
        Patient,
        id
    )


    if not patient:

        return jsonify({
            "success": False,
            "message": "Patient not found"
        }), 404


    data = request.get_json()


    if not data:

        return jsonify({
            "success": False,
            "message": "JSON data is required"
        }), 400


    required_fields = [
        "name",
        "age",
        "gender",
        "contact"
    ]


    for field in required_fields:

        if field not in data:

            return jsonify({
                "success": False,
                "message": f"{field} is required"
            }), 400


    patient.name = data["name"]

    patient.age = data["age"]

    patient.gender = data["gender"]

    patient.contact = data["contact"]


    db.session.commit()


    return jsonify({
        "success": True,
        "message": "Patient updated successfully",
        "patient": patient.to_dict()
    })


# ---------------------------------------------------------
# PATCH /api/patients/<id>
# Partial update
# ---------------------------------------------------------

@patients_bp.route(
    "/api/patients/<int:id>",
    methods=["PATCH"]
)
@admin_required()
def api_patch_patient(id):

    patient = db.session.get(
        Patient,
        id
    )


    if not patient:

        return jsonify({
            "success": False,
            "message": "Patient not found"
        }), 404


    data = request.get_json()


    if not data:

        return jsonify({
            "success": False,
            "message": "JSON data is required"
        }), 400


    if "name" in data:

        patient.name = data["name"]


    if "age" in data:

        patient.age = data["age"]


    if "gender" in data:

        patient.gender = data["gender"]


    if "contact" in data:

        patient.contact = data["contact"]


    db.session.commit()


    return jsonify({
        "success": True,
        "message": "Patient updated successfully",
        "patient": patient.to_dict()
    })


# ---------------------------------------------------------
# DELETE /api/patients/<id>
# Delete patient
# ---------------------------------------------------------

@patients_bp.route(
    "/api/patients/<int:id>",
    methods=["DELETE"]
)
@admin_required()
def api_delete_patient(id):

    patient = db.session.get(
        Patient,
        id
    )


    if not patient:

        return jsonify({
            "success": False,
            "message": "Patient not found"
        }), 404


    db.session.delete(patient)

    db.session.commit()


    return jsonify({
        "success": True,
        "message": "Patient deleted successfully"
    })


# =========================================================
# WEB DELETE
# =========================================================

@patients_bp.route(
    "/patients/<int:id>",
    methods=["DELETE"]
)
def patient_delete(id):

    try:

        verify_jwt_in_request()

    except Exception:

        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401


    patient = db.session.get(
        Patient,
        id
    )


    if not patient:

        return jsonify({
            "success": False,
            "message": "Patient not found"
        }), 404


    db.session.delete(patient)

    db.session.commit()


    return jsonify({
        "success": True,
        "message": "Patient deleted successfully"
    })