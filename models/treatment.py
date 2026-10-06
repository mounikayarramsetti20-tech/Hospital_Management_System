from . import db


class Treatment(db.Model):
    __tablename__ = "treatments"

    id = db.Column(db.Integer, primary_key=True)

    appointment_id = db.Column(
        db.Integer,
        db.ForeignKey("appointments.id"),
        nullable=False
    )

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.id"),
        nullable=False
    )

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.id"),
        nullable=False
    )

    treatment = db.Column(
        db.String(255),
        nullable=False
    )

    medicine = db.Column(
        db.String(255),
        nullable=True
    )

    notes = db.Column(
        db.Text,
        nullable=True
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="Ongoing"
    )

    appointment = db.relationship(
        "Appointment",
        backref="treatments"
    )

    patient = db.relationship(
        "Patient",
        backref="treatments"
    )

    doctor = db.relationship(
        "Doctor",
        backref="treatments"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "appointment_id": self.appointment_id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "treatment": self.treatment,
            "medicine": self.medicine,
            "notes": self.notes,
            "status": self.status
        }