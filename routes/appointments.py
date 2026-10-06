from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import verify_jwt_in_request, get_jwt

from models import db
from models.appointment import Appointment
from models.patient import Patient
from models.doctor import Doctor

from routes import doctor_or_admin_required, admin_required


appointments_bp = Blueprint(
    "appointments",
    __name__
)


# ============================================================
# HELPER
# ============================================================

def doctor_can_access(appointment, claims):

    role = claims.get("role")

    if role == "admin":
        return True

    if role == "doctor":

        doctor_id = claims.get("doctor_id")

        if doctor_id is None:
            return False

        return int(doctor_id) == int(
            appointment.doctor_id
        )

    return False


# ============================================================
# PAGE ROUTES
# ============================================================

@appointments_bp.route(
    "/appointments/",
    methods=["GET"]
)
def list_page():

    return render_template(
        "appointments/list.html"
    )


@appointments_bp.route(
    "/appointments/new",
    methods=["GET"]
)
def new_page():

    return render_template(
        "appointments/form.html"
    )


@appointments_bp.route(
    "/appointments/<int:appointment_id>",
    methods=["GET"]
)
def view_page(appointment_id):

    # Do NOT check JWT here.
    # The browser cannot automatically send
    # localStorage JWT during page navigation.

    return render_template(
        "appointments/view.html",
        appointment_id=appointment_id
    )


@appointments_bp.route(
    "/appointments/<int:appointment_id>/edit",
    methods=["GET"]
)
def edit_page(appointment_id):

    # The edit page will use the protected API
    # from JavaScript.

    return render_template(
        "appointments/form.html",
        appointment_id=appointment_id
    )


# ============================================================
# API - GET ALL APPOINTMENTS
# ============================================================

@appointments_bp.route(
    "/api/appointments",
    methods=["GET"]
)
def get_appointments():

    try:

        verify_jwt_in_request()

        claims = get_jwt()

    except Exception:

        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401

    role = claims.get("role")

    if role == "admin":

        appointments = Appointment.query.order_by(
            Appointment.id.asc()
        ).all()

    elif role == "doctor":

        doctor_id = claims.get(
            "doctor_id"
        )

        if doctor_id is None:

            return jsonify({
                "success": False,
                "message": "Doctor account is not linked to a doctor"
            }), 403

        appointments = Appointment.query.filter_by(
            doctor_id=int(doctor_id)
        ).order_by(
            Appointment.id.asc()
        ).all()

    else:

        return jsonify({
            "success": False,
            "message": "Access denied"
        }), 403

    return jsonify({
        "success": True,
        "appointments": [
            appointment.to_dict()
            for appointment in appointments
        ]
    })


# ============================================================
# API - GET SINGLE APPOINTMENT
# ============================================================

@appointments_bp.route(
    "/api/appointments/<int:appointment_id>",
    methods=["GET"]
)
def get_appointment(appointment_id):

    try:

        verify_jwt_in_request()

        claims = get_jwt()

    except Exception:

        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401

    appointment = db.session.get(
        Appointment,
        appointment_id
    )

    if not appointment:

        return jsonify({
            "success": False,
            "message": "Appointment not found"
        }), 404

    if not doctor_can_access(
        appointment,
        claims
    ):

        return jsonify({
            "success": False,
            "message": "Access denied"
        }), 403

    return jsonify({
        "success": True,
        "appointment": appointment.to_dict()
    })


# ============================================================
# API - CREATE APPOINTMENT
# ============================================================

@appointments_bp.route(
    "/api/appointments",
    methods=["POST"]
)
@doctor_or_admin_required()
def create_appointment():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "JSON data is required"
        }), 400

    patient_id = data.get(
        "patient_id"
    )

    doctor_id = data.get(
        "doctor_id"
    )

    date = data.get(
        "date"
    )

    diagnosis = data.get(
        "diagnosis"
    )

    status = data.get(
        "status",
        "Under Treatment"
    )

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

    if not date:

        return jsonify({
            "success": False,
            "message": "Appointment date is required"
        }), 400

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
                "message": "Doctor can only create appointments for their own doctor account"
            }), 403

    from datetime import datetime

    try:

        appointment_date = datetime.fromisoformat(
            date.replace("Z", "+00:00")
        )

    except ValueError:

        return jsonify({
            "success": False,
            "message": "Invalid date format"
        }), 400

    new_appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        date=appointment_date,
        diagnosis=diagnosis,
        status=status
    )

    db.session.add(
        new_appointment
    )

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Appointment created successfully",
        "appointment": new_appointment.to_dict()
    }), 201


# ============================================================
# API - UPDATE APPOINTMENT
# ============================================================

@appointments_bp.route(
    "/api/appointments/<int:appointment_id>",
    methods=["PUT", "PATCH"]
)
@doctor_or_admin_required()
def update_appointment(appointment_id):

    appointment = db.session.get(
        Appointment,
        appointment_id
    )

    if not appointment:

        return jsonify({
            "success": False,
            "message": "Appointment not found"
        }), 404

    claims = get_jwt()

    if not doctor_can_access(
        appointment,
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
        appointment.doctor_id
    )

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
                "message": "Doctor cannot assign appointment to another doctor"
            }), 403

    patient_id = data.get(
        "patient_id",
        appointment.patient_id
    )

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
        new_doctor_id
    )

    if not doctor:

        return jsonify({
            "success": False,
            "message": "Doctor not found"
        }), 404

    appointment.patient_id = patient_id
    appointment.doctor_id = new_doctor_id

    if "date" in data:

        from datetime import datetime

        try:

            appointment.date = datetime.fromisoformat(
                data["date"].replace(
                    "Z",
                    "+00:00"
                )
            )

        except ValueError:

            return jsonify({
                "success": False,
                "message": "Invalid date format"
            }), 400

    if "diagnosis" in data:

        appointment.diagnosis = data[
            "diagnosis"
        ]

    if "status" in data:

        appointment.status = data[
            "status"
        ]

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Appointment updated successfully",
        "appointment": appointment.to_dict()
    })


# ============================================================
# API - DELETE APPOINTMENT
# ============================================================

@appointments_bp.route(
    "/api/appointments/<int:appointment_id>",
    methods=["DELETE"]
)
@admin_required()
def delete_appointment(appointment_id):

    appointment = db.session.get(
        Appointment,
        appointment_id
    )

    if not appointment:

        return jsonify({
            "success": False,
            "message": "Appointment not found"
        }), 404

    db.session.delete(
        appointment
    )

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Appointment deleted successfully"
    })