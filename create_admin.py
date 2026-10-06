from app import app
from models import db
from models.user import User


with app.app_context():

    username = "admin"
    password = "admin123"

    existing_user = User.query.filter_by(
        username=username
    ).first()

    if existing_user:

        print("Admin user already exists.")

    else:

        admin = User(
            username=username,
            role="admin"
        )

        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        print("Admin user created successfully.")
        print("Username: admin")
        print("Password: admin123")