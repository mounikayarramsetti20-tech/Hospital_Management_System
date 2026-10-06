from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import verify_jwt_in_request, get_jwt

from models import db
from models.treatment import Treatment
from models.appointment import Appointment
from models.patient import Patient
from models.doctor import Doctor

from routes import doctor_or_admin_required, admin_required


treatments_bp = Blueprint(
    "treatments",
    __name__
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def doctor_can_access(treatment, claims):

    role = claims.get("role")

    if role == "admin":
        return True

    if role == "doctor":

        doctor_id = claims.get("doctor_id")

        if doctor_id is None:
            return False

        return int(doctor_id) == int(treatment.doctor_id)

    return False


# ============================================================
# PAGE ROUTES
# ============================================================

@treatments_bp.route(
    "/treatments/",
    methods=["GET"]
)
def list_page():

    return render_template(
        "treatments/list.html"
    )


@treatments_bp.route(
    "/treatments/new",
    methods=["GET"]
)
def new_page():

    try:
        verify_jwt_in_request()

    except Exception:
        return render_template(
            "login.html"
        )

    return render_template(
        "treatments/form.html"
    )


@treatments_bp.route(
    "/treatments/<int:treatment_id>",
    methods=["GET"]
)
def view_page(treatment_id):

    try:

        verify_jwt_in_request()

        claims = get_jwt()

    except Exception:

        return render_template(
            "login.html"
        )

    treatment = db.session.get(
        Treatment,
        treatment_id
    )

    if not treatment:

        return (
            "Treatment not found",
            404
        )

    if not doctor_can_access(
        treatment,
        claims
    ):

        return (
            "Access denied. You are not allowed to view this treatment.",
            403
        )

    return render_template(
        "treatments/view.html",
        treatment=treatment
    )


@treatments_bp.route(
    "/treatments/<int:treatment_id>/edit",
    methods=["GET"]
)
def edit_page(treatment_id):

    try:

        verify_jwt_in_request()

        claims = get_jwt()

    except Exception:

        return render_template(
            "login.html"
        )

    treatment = db.session.get(
        Treatment,
        treatment_id
    )

    if not treatment:

        return (
            "Treatment not found",
            404
        )

    if not doctor_can_access(
        treatment,
        claims
    ):

        return (
            "Access denied. You are not allowed to edit this treatment.",
            403
        )

    return render_template(
        "treatments/form.html",
        treatment=treatment
    )


# ============================================================
# API - GET ALL TREATMENTS
# ============================================================

@treatments_bp.route(
    "/api/treatments",
    methods=["GET"]
)
def get_treatments():

    try:

        verify_jwt_in_request()

        claims = get_jwt()

    except Exception:

        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401

    role = claims.get("role")

    # -------------------------
    # ADMIN
    # -------------------------

    if role == "admin":

        treatments = Treatment.query.order_by(
            Treatment.id.asc()
        ).all()

    # -------------------------
    # DOCTOR
    # -------------------------

    elif role == "doctor":

        doctor_id = claims.get(
            "doctor_id"
        )

        if doctor_id is None:

            return jsonify({
                "success": False,
                "message": "Doctor account is not linked to a doctor"
            }), 403

        treatments = Treatment.query.filter_by(
            doctor_id=int(doctor_id)
        ).order_by(
            Treatment.id.asc()
        ).all()

    # -------------------------
    # OTHER USERS
    # -------------------------

    else:

        return jsonify({
            "success": False,
            "message": "Access denied"
        }), 403

    return jsonify({
        "success": True,
        "treatments": [
            treatment.to_dict()
            for treatment in treatments
        ]
    })


# ============================================================
# API - GET SINGLE TREATMENT
# ============================================================

@treatments_bp.route(
    "/api/treatments/<int:treatment_id>",
    methods=["GET"]
)
def get_treatment(treatment_id):

    try:

        verify_jwt_in_request()

        claims = get_jwt()

    except Exception:

        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401

    treatment = db.session.get(
        Treatment,
        treatment_id
    )

    if not treatment:

        return jsonify({
            "success": False,
            "message": "Treatment not found"
        }), 404

    if not doctor_can_access(
        treatment,
        claims
    ):

        return jsonify({
            "success": False,
            "message": "Access denied"
        }), 403

    return jsonify({
        "success": True,
        "treatment": treatment.to_dict()
    })


# ============================================================
# API - CREATE TREATMENT
# ============================================================

@treatments_bp.route(
    "/api/treatments",
    methods=["POST"]
)
@doctor_or_admin_required()
def create_treatment():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "JSON data is required"
        }), 400

    appointment_id = data.get(
        "appointment_id"
    )

    patient_id = data.get(
        "patient_id"
    )

    doctor_id = data.get(
        "doctor_id"
    )

    treatment_name = data.get(
        "treatment"
    )

    medicine = data.get(
        "medicine"
    )

    notes = data.get(
        "notes"
    )

    status = data.get(
        "status",
        "Ongoing"
    )

    if not appointment_id:

        return jsonify({
            "success": False,
            "message": "Appointment ID is required"
        }), 400

    if not patient_id:

        return jsonify({
            "success": False,
            "message": "Patient ID is required"
        }), 400

    if not doctor_id:

        return jsonify({
            "success": False,
            "message": "Doctor ID is required"
        }), 400

    if not treatment_name:

        return jsonify({
            "success": False,
            "message": "Treatment is required"
        }), 400

    appointment = db.session.get(
        Appointment,
        appointment_id
    )

    if not appointment:

        return jsonify({
            "success": False,
            "message": "Appointment not found"
        }), 404

    patient = db.session.get(
        Patient,
        patient_id
    )

    if not patient:

        return jsonify({
            "success": False,
            "message": "Patient not found"
        }), 404

    doctor = db.session.get(
        Doctor,
        doctor_id
    )

    if not doctor:

        return jsonify({
            "success": False,
            "message": "Doctor not found"
        }), 404

    claims = get_jwt()

    role = claims.get(
        "role"
    )

    # Doctor can only create treatment
    # for their own doctor account.

    if role == "doctor":

        own_doctor_id = claims.get(
            "doctor_id"
        )

        if own_doctor_id is None:

            return jsonify({
                "success": False,
                "message": "Doctor account is not linked"
            }), 403

        if int(doctor_id) != int(
            own_doctor_id
        ):

            return jsonify({
                "success": False,
                "message": "Doctor can only create treatment for their own doctor account"
            }), 403

    # Treatment doctor must match appointment doctor.

    if appointment.doctor_id != int(
        doctor_id
    ):

        return jsonify({
            "success": False,
            "message": "Treatment doctor must match appointment doctor"
        }), 400

    # Treatment patient must match appointment patient.

    if appointment.patient_id != int(
        patient_id
    ):

        return jsonify({
            "success": False,
            "message": "Treatment patient must match appointment patient"
        }), 400

    new_treatment = Treatment(
        appointment_id=appointment_id,
        patient_id=patient_id,
        doctor_id=doctor_id,
        treatment=treatment_name,
        medicine=medicine,
        notes=notes,
        status=status
    )

    db.session.add(
        new_treatment
    )

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Treatment created successfully",
        "treatment": new_treatment.to_dict()
    }), 201


# ============================================================
# API - UPDATE TREATMENT
# ============================================================

@treatments_bp.route(
    "/api/treatments/<int:treatment_id>",
    methods=["PUT", "PATCH"]
)
@doctor_or_admin_required()
def update_treatment(treatment_id):

    treatment = db.session.get(
        Treatment,
        treatment_id
    )

    if not treatment:

        return jsonify({
            "success": False,
            "message": "Treatment not found"
        }), 404

    claims = get_jwt()

    if not doctor_can_access(
        treatment,
        claims
    ):

        return jsonify({
            "success": False,
            "message": "Access denied"
        }), 403

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "JSON data is required"
        }), 400

    role = claims.get(
        "role"
    )

    new_doctor_id = data.get(
        "doctor_id",
        treatment.doctor_id
    )

    # Doctor cannot assign treatment
    # to another doctor.

    if role == "doctor":

        own_doctor_id = claims.get(
            "doctor_id"
        )

        if own_doctor_id is None:

            return jsonify({
                "success": False,
                "message": "Doctor account is not linked"
            }), 403

        if int(new_doctor_id) != int(
            own_doctor_id
        ):

            return jsonify({
                "success": False,
                "message": "Doctor cannot assign treatment to another doctor"
            }), 403

    appointment_id = data.get(
        "appointment_id",
        treatment.appointment_id
    )

    patient_id = data.get(
        "patient_id",
        treatment.patient_id
    )

    appointment = db.session.get(
        Appointment,
        appointment_id
    )

    if not appointment:

        return jsonify({
            "success": False,
            "message": "Appointment not found"
        }), 404

    patient = db.session.get(
        Patient,
        patient_id
    )

    if not patient:

        return jsonify({
            "success": False,
            "message": "Patient not found"
        }), 404

    if appointment.doctor_id != int(
        new_doctor_id
    ):

        return jsonify({
            "success": False,
            "message": "Treatment doctor must match appointment doctor"
        }), 400

    if appointment.patient_id != int(
        patient_id
    ):

        return jsonify({
            "success": False,
            "message": "Treatment patient must match appointment patient"
        }), 400

    treatment.appointment_id = appointment_id
    treatment.patient_id = patient_id
    treatment.doctor_id = new_doctor_id

    if "treatment" in data:

        treatment.treatment = data[
            "treatment"
        ]

    if "medicine" in data:

        treatment.medicine = data[
            "medicine"
        ]

    if "notes" in data:

        treatment.notes = data[
            "notes"
        ]

    if "status" in data:

        treatment.status = data[
            "status"
        ]

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Treatment updated successfully",
        "treatment": treatment.to_dict()
    })


# ============================================================
# API - DELETE TREATMENT
# ============================================================

@treatments_bp.route(
    "/api/treatments/<int:treatment_id>",
    methods=["DELETE"]
)
@admin_required()
def delete_treatment(treatment_id):

    treatment = db.session.get(
        Treatment,
        treatment_id
    )

    if not treatment:

        return jsonify({
            "success": False,
            "message": "Treatment not found"
        }), 404

    db.session.delete(
        treatment
    )

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Treatment deleted successfully"
    })