# 🏥 CarePoint – Hospital Patient Record and Treatment Tracking System

CarePoint is a web-based **Hospital Patient Record and Treatment Tracking System** developed using **Flask, MySQL, SQLAlchemy, JWT Authentication, Pandas, NumPy, HTML, CSS, and JavaScript**.

The system helps hospitals manage patients, doctors, appointments, treatments, analytics, and patient data import/export through a centralized web application.

---

## 📌 Project Overview

The Hospital Patient Record and Treatment Tracking System provides a secure and organized platform for managing hospital records.

The system supports:

- Patient management
- Doctor management
- Appointment management
- Treatment tracking
- Hospital analytics
- CSV data import/export
- Excel data import/export
- JWT-based authentication
- Role-based access control
- Admin and Doctor accounts
- REST API endpoints
- Responsive web interface

The application is designed with a modern **CarePoint** healthcare interface using an emerald/teal visual theme.

---

## ✨ Features

### 👨‍⚕️ Patient Management

- Add new patients
- View patient records
- Edit patient information
- Delete patient records
- Store:
  - Patient name
  - Age
  - Gender
  - Contact information

---

### 🩺 Doctor Management

- Add doctors
- View doctor information
- Edit doctor information
- Delete doctors
- Store:
  - Doctor name
  - Specialization
  - Contact
  - Email

---

### 📅 Appointment Management

- Create appointments
- View appointments
- Edit appointments
- Delete appointments
- Assign patients to doctors
- Store diagnosis
- Track appointment status

Supported statuses include:

- Scheduled
- Under Treatment
- Completed
- Cancelled

---

### 💊 Treatment Tracking

- Create treatment records
- View treatment details
- Edit treatments
- Delete treatments
- Link treatments with appointments
- Link treatments with patients
- Link treatments with doctors
- Store medicines and treatment notes

Supported treatment statuses include:

- Ongoing
- Completed
- Cancelled

---

## 🔐 Authentication & Security

The application uses **JWT (JSON Web Token) authentication**.

### User Roles

#### Admin

Administrators have full access to the system.

Admin permissions include:

- Manage patients
- Manage doctors
- Manage appointments
- Manage treatments
- Delete appointments
- Delete treatments
- Access analytics
- Import patient data
- Export patient data

#### Doctor

Doctors have restricted access to their own records.

Doctor permissions include:

- View assigned appointments
- Create appointments
- Edit own appointments
- View assigned treatments
- Create treatments
- Edit own treatments

Doctors cannot delete records or access another doctor's records.

---

## 📊 Analytics Dashboard

The application provides a hospital analytics dashboard using **Pandas and NumPy**.

Analytics include:

### Patient Analytics

- Total patients
- Average patient age
- Minimum age
- Maximum age
- Male patients
- Female patients
- Age standard deviation
- Gender distribution

### Appointment Analytics

- Total appointments
- Appointment status distribution

### Treatment Analytics

- Total treatments
- Treatment status distribution

### Doctor Analytics

- Doctor-wise appointment count
- Doctor specialization

---

## 📁 Data Import & Export

The system supports patient data management through CSV and Excel files.

### Export

Patient records can be exported as:

- CSV
- Excel

### Import

Patient records can be imported from:

- CSV
- Excel (`.xlsx`, `.xls`)

The system also reports:

- Number of imported records
- Number of skipped records
- Import errors

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| MySQL | Database |
| SQLAlchemy | ORM and database management |
| Flask-JWT-Extended | JWT authentication |
| Flask-Migrate | Database migration support |
| PyMySQL | MySQL database connection |
| Pandas | Data analysis and import/export |
| NumPy | Statistical calculations |
| OpenPyXL | Excel file processing |
| HTML5 | Frontend structure |
| CSS3 | Frontend styling |
| JavaScript | Frontend functionality |
| Jinja2 | HTML templating |

---

## 📂 Project Structure

```text
hospital_management/
│
├── app.py
├── config.py
├── create_admin.py
├── create_doctor.py
├── requirements.txt
├── .env
├── .gitignore
│
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── patient.py
│   ├── doctor.py
│   ├── appointment.py
│   └── treatment.py
│
├── routes/
│   ├── __init__.py
│   ├── home.py
│   ├── auth.py
│   ├── patients.py
│   ├── doctors.py
│   ├── appointments.py
│   ├── treatments.py
│   └── data.py
│
├── templates/
│   ├── home.html
│   ├── login.html
│   ├── analytics.html
│   ├── data.html
│   │
│   ├── patients/
│   │   ├── list.html
│   │   ├── form.html
│   │   └── view.html
│   │
│   ├── doctors/
│   │   ├── list.html
│   │   ├── form.html
│   │   └── view.html
│   │
│   ├── appointments/
│   │   ├── list.html
│   │   ├── form.html
│   │   └── view.html
│   │
│   └── treatments/
│       ├── list.html
│       ├── form.html
│       └── view.html
│
└── static/
    ├── style.css
    └── script.js
