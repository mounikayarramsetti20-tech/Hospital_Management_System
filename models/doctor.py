from models import db


class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    specialization = db.Column(
        db.String(100),
        nullable=False
    )

    contact = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    # Relationship with User
    user = db.relationship(
        "User",
        back_populates="doctor",
        uselist=False
    )

    # Relationship with Appointments
    appointments = db.relationship(
        "Appointment",
        back_populates="doctor",
        lazy=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "specialization": self.specialization,
            "contact": self.contact,
            "email": self.email
        }