from app import app
from models import db
from models.user import User
from models.doctor import Doctor


with app.app_context():

    # Find the first doctor in the database
    doctor = Doctor.query.order_by(
        Doctor.id.asc()
    ).first()

    if not doctor:

        print("No doctor found.")
        print("Please create a doctor first.")
        exit()

    username = "doctor"
    password = "doctor123"

    # Check whether account already exists
    existing_user = User.query.filter_by(
        username=username
    ).first()

    if existing_user:

        print("Doctor user already exists.")

    else:

        doctor_user = User(
            username=username,
            role="doctor",
            doctor_id=doctor.id
        )

        doctor_user.set_password(password)

        db.session.add(doctor_user)

        db.session.commit()

        print("Doctor user created successfully.")
        print()
        print("Username:", username)
        print("Password:", password)
        print("Doctor ID:", doctor.id)
        print("Doctor Name:", doctor.name)
        print("Specialization:", doctor.specialization)