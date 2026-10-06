from flask import (
    Blueprint,
    request,
    jsonify,
    send_file,
    render_template
)

from models import db
from models.patient import Patient
from models.appointment import Appointment
from models.treatment import Treatment
from models.doctor import Doctor

import pandas as pd
import numpy as np
import io


data_bp = Blueprint("data", __name__)


# =========================================================
# DATA IMPORT / EXPORT PAGE
# =========================================================

@data_bp.route("/data", methods=["GET"])
def data_page():
    return render_template("data.html")


# =========================================================
# ANALYTICS PAGE
# =========================================================

@data_bp.route("/analytics", methods=["GET"])
def analytics_page():
    return render_template("analytics.html")


# =========================================================
# EXPORT PATIENTS TO CSV
# =========================================================

@data_bp.route("/api/export/patients/csv", methods=["GET"])
def export_patients_csv():

    patients = Patient.query.order_by(
        Patient.id.asc()
    ).all()

    data = []

    for patient in patients:
        data.append({
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "contact": patient.contact
        })

    df = pd.DataFrame(data)

    csv_data = df.to_csv(index=False)

    output = io.BytesIO(
        csv_data.encode("utf-8")
    )

    output.seek(0)

    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name="patients.csv"
    )


# =========================================================
# EXPORT PATIENTS TO EXCEL
# =========================================================

@data_bp.route("/api/export/patients/excel", methods=["GET"])
def export_patients_excel():

    patients = Patient.query.order_by(
        Patient.id.asc()
    ).all()

    data = []

    for patient in patients:
        data.append({
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "contact": patient.contact
        })

    df = pd.DataFrame(data)

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Patients"
        )

    output.seek(0)

    return send_file(
        output,
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        as_attachment=True,
        download_name="patients.xlsx"
    )


# =========================================================
# IMPORT PATIENTS FROM CSV
# =========================================================

@data_bp.route("/api/import/patients/csv", methods=["POST"])
def import_patients_csv():

    if "file" not in request.files:
        return jsonify({
            "success": False,
            "message": "CSV file is required"
        }), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "success": False,
            "message": "No file selected"
        }), 400

    try:
        df = pd.read_csv(file)

    except Exception as error:
        return jsonify({
            "success": False,
            "message": (
                "Unable to read CSV file: "
                + str(error)
            )
        }), 400

    required_columns = [
        "name",
        "age",
        "gender",
        "contact"
    ]

    for column in required_columns:

        if column not in df.columns:
            return jsonify({
                "success": False,
                "message": "Missing column: " + column
            }), 400

    imported = 0
    skipped = 0

    for _, row in df.iterrows():

        try:

            if (
                pd.isna(row["name"])
                or pd.isna(row["age"])
                or pd.isna(row["gender"])
                or pd.isna(row["contact"])
            ):
                skipped += 1
                continue

            name = str(row["name"]).strip()
            age = int(float(row["age"]))
            gender = str(row["gender"]).strip()
            contact = str(row["contact"]).strip()

        except (ValueError, TypeError):

            skipped += 1
            continue

        if not name or not gender or not contact:
            skipped += 1
            continue

        existing_patient = Patient.query.filter_by(
            contact=contact
        ).first()

        if existing_patient:
            skipped += 1
            continue

        patient = Patient(
            name=name,
            age=age,
            gender=gender,
            contact=contact
        )

        db.session.add(patient)

        imported += 1

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "CSV import completed",
        "imported": imported,
        "skipped": skipped
    })


# =========================================================
# IMPORT PATIENTS FROM EXCEL
# =========================================================

@data_bp.route("/api/import/patients/excel", methods=["POST"])
def import_patients_excel():

    if "file" not in request.files:
        return jsonify({
            "success": False,
            "message": "Excel file is required"
        }), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "success": False,
            "message": "No file selected"
        }), 400

    try:
        df = pd.read_excel(file)

    except Exception as error:
        return jsonify({
            "success": False,
            "message": (
                "Unable to read Excel file: "
                + str(error)
            )
        }), 400

    required_columns = [
        "name",
        "age",
        "gender",
        "contact"
    ]

    for column in required_columns:

        if column not in df.columns:
            return jsonify({
                "success": False,
                "message": "Missing column: " + column
            }), 400

    imported = 0
    skipped = 0

    for _, row in df.iterrows():

        try:

            if (
                pd.isna(row["name"])
                or pd.isna(row["age"])
                or pd.isna(row["gender"])
                or pd.isna(row["contact"])
            ):
                skipped += 1
                continue

            name = str(row["name"]).strip()
            age = int(float(row["age"]))
            gender = str(row["gender"]).strip()
            contact = str(row["contact"]).strip()

        except (ValueError, TypeError):

            skipped += 1
            continue

        if not name or not gender or not contact:
            skipped += 1
            continue

        existing_patient = Patient.query.filter_by(
            contact=contact
        ).first()

        if existing_patient:
            skipped += 1
            continue

        patient = Patient(
            name=name,
            age=age,
            gender=gender,
            contact=contact
        )

        db.session.add(patient)

        imported += 1

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Excel import completed",
        "imported": imported,
        "skipped": skipped
    })


# =========================================================
# COMPLETE HOSPITAL ANALYTICS
# =========================================================

@data_bp.route(
    "/api/analytics/hospital",
    methods=["GET"]
)
def hospital_analytics():

    # -----------------------------------------------------
    # PATIENT DATA
    # -----------------------------------------------------

    patients = Patient.query.all()

    patient_data = []

    for patient in patients:

        patient_data.append({
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "contact": patient.contact
        })

    patient_df = pd.DataFrame(patient_data)

    # -----------------------------------------------------
    # PATIENT ANALYTICS
    # -----------------------------------------------------

    if len(patient_df) > 0:

        ages = np.array(
            patient_df["age"],
            dtype=float
        )

        average_age = float(
            np.mean(ages)
        )

        minimum_age = int(
            np.min(ages)
        )

        maximum_age = int(
            np.max(ages)
        )

        age_std = float(
            np.std(ages)
        )

        gender_distribution = (
            patient_df["gender"]
            .value_counts()
            .to_dict()
        )

        male_patients = int(
            (
                patient_df["gender"]
                .str.lower()
                == "male"
            ).sum()
        )

        female_patients = int(
            (
                patient_df["gender"]
                .str.lower()
                == "female"
            ).sum()
        )

    else:

        average_age = 0
        minimum_age = 0
        maximum_age = 0
        age_std = 0
        gender_distribution = {}
        male_patients = 0
        female_patients = 0


    # -----------------------------------------------------
    # APPOINTMENT DATA
    # -----------------------------------------------------

    appointments = Appointment.query.all()

    appointment_data = []

    for appointment in appointments:

        appointment_data.append({
            "id": appointment.id,
            "patient_id": appointment.patient_id,
            "doctor_id": appointment.doctor_id,
            "date": appointment.date.isoformat(),
            "diagnosis": appointment.diagnosis,
            "status": appointment.status
        })

    appointment_df = pd.DataFrame(
        appointment_data
    )


    # -----------------------------------------------------
    # APPOINTMENT STATUS ANALYSIS
    # -----------------------------------------------------

    if len(appointment_df) > 0:

        appointment_status_distribution = (
            appointment_df["status"]
            .value_counts()
            .to_dict()
        )

    else:

        appointment_status_distribution = {}


    # -----------------------------------------------------
    # TREATMENT DATA
    # -----------------------------------------------------

    treatments = Treatment.query.all()

    treatment_data = []

    for treatment in treatments:

        treatment_data.append({
            "id": treatment.id,
            "appointment_id":
                treatment.appointment_id,
            "patient_id":
                treatment.patient_id,
            "doctor_id":
                treatment.doctor_id,
            "treatment":
                treatment.treatment,
            "medicine":
                treatment.medicine,
            "status":
                treatment.status
        })

    treatment_df = pd.DataFrame(
        treatment_data
    )


    # -----------------------------------------------------
    # TREATMENT STATUS ANALYSIS
    # -----------------------------------------------------

    if len(treatment_df) > 0:

        treatment_status_distribution = (
            treatment_df["status"]
            .value_counts()
            .to_dict()
        )

    else:

        treatment_status_distribution = {}


    # -----------------------------------------------------
    # DOCTOR DATA
    # -----------------------------------------------------

    doctors = Doctor.query.all()

    doctor_data = []

    for doctor in doctors:

        doctor_data.append({
            "id": doctor.id,
            "name": doctor.name,
            "specialization":
                doctor.specialization
        })

    doctor_df = pd.DataFrame(
        doctor_data
    )


    # -----------------------------------------------------
    # DOCTOR-WISE APPOINTMENT COUNT
    # -----------------------------------------------------

    doctor_appointments = []

    for doctor in doctors:

        count = Appointment.query.filter_by(
            doctor_id=doctor.id
        ).count()

        doctor_appointments.append({
            "doctor_id": doctor.id,
            "doctor_name": doctor.name,
            "specialization":
                doctor.specialization,
            "appointment_count": count
        })


    # -----------------------------------------------------
    # FINAL ANALYTICS
    # -----------------------------------------------------

    analytics = {

        "patients": {

            "total": len(patient_df),

            "average_age":
                round(average_age, 2),

            "minimum_age":
                minimum_age,

            "maximum_age":
                maximum_age,

            "age_standard_deviation":
                round(age_std, 2),

            "male":
                male_patients,

            "female":
                female_patients,

            "gender_distribution":
                gender_distribution
        },


        "appointments": {

            "total":
                len(appointment_df),

            "status_distribution":
                appointment_status_distribution
        },


        "treatments": {

            "total":
                len(treatment_df),

            "status_distribution":
                treatment_status_distribution
        },


        "doctors": {

            "total":
                len(doctor_df),

            "doctor_appointments":
                doctor_appointments
        }

    }


    return jsonify({
        "success": True,
        "analytics": analytics
    })


# =========================================================
# OLD PATIENT ANALYTICS API
# =========================================================

@data_bp.route(
    "/api/analytics/patients",
    methods=["GET"]
)
def patient_analytics():

    patients = Patient.query.all()

    if not patients:

        return jsonify({
            "success": True,
            "message":
                "No patient data available",

            "analytics": {

                "total_patients": 0,

                "average_age": 0,

                "minimum_age": 0,

                "maximum_age": 0,

                "age_standard_deviation": 0,

                "male_patients": 0,

                "female_patients": 0,

                "gender_distribution": {}
            }
        })


    data = []

    for patient in patients:

        data.append({
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "contact": patient.contact
        })


    df = pd.DataFrame(data)

    ages = np.array(
        df["age"],
        dtype=float
    )


    gender_counts = (
        df["gender"]
        .str.lower()
        .value_counts()
    )


    analytics = {

        "total_patients":
            int(len(df)),

        "average_age":
            round(
                float(np.mean(ages)),
                2
            ),

        "minimum_age":
            int(np.min(ages)),

        "maximum_age":
            int(np.max(ages)),

        "age_standard_deviation":
            round(
                float(np.std(ages)),
                2
            ),

        "male_patients":
            int(
                gender_counts.get(
                    "male",
                    0
                )
            ),

        "female_patients":
            int(
                gender_counts.get(
                    "female",
                    0
                )
            ),

        "gender_distribution":
            df["gender"]
            .value_counts()
            .to_dict()
    }


    return jsonify({
        "success": True,
        "analytics": analytics
    })