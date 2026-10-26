# CourseHub

A role-based online course management platform built with **Django 5** and **Bootstrap 5**.
CourseHub supports four user types (Admin, Data Analyst, Instructor and Student), each with its own dashboard and permissions. It covers course creation, enrollment, content delivery and analytics.

## Features

**Role-based access control**
- Custom authentication with hashed passwords (Django's `make_password` / `check_password`) and session-based login
- One central credentials table linked to separate profile tables for each role
- A dashboard for each role, with views that check the user's role before granting access

**Admin**
- Create, edit and delete courses (certificate, diploma or degree programs)
- Assign or remove instructors and students on any course
- Create users, promote users to admin and delete accounts

**Instructor**
- View assigned courses
- Add and update course content (videos and notes) for courses they teach

**Student**
- Browse the course catalog and view course details
- Enroll in and unenroll from courses
- Track enrolled courses and evaluations under "My Courses"
- Manage their profile (age, skill level, nationality and more)

**Data Analyst**
- Platform-wide KPIs: total courses, students, instructors and enrollments
- Most popular courses by enrollment, and average evaluation scores by course
- Student demographics by nationality and skill level, plus how many courses each student is enrolled in

**Other details**
- Relational schema with many-to-many relationships: courses ↔ topics, books, partner universities, instructors and students
- Custom `NoCacheMiddleware` stops users from seeing cached pages with the browser's back button after logging out
- Seed script that fills the database with realistic demo data

## Tech Stack

| Layer    | Technology                                       |
|----------|--------------------------------------------------|
| Backend  | Python 3, Django 5.0                             |
| Database | SQLite (Django ORM)                              |
| Frontend | Django Templates, Bootstrap 5.3, Bootstrap Icons |

## Project Structure

```
course_platform/
├── accounts/        # Authentication, roles, dashboards, user & course management
├── courses/         # Course catalog, enrollment, instructor content
├── analytics/       # Analyst statistics & demographics
├── course_platform/ # Project settings and URL routing
├── templates/       # HTML templates (Bootstrap 5)
├── static/
└── seed_data.py     # Demo data generator
```

## Getting Started

### Prerequisites
- Python 3.10+
- pip

### Setup

```bash
git clone <your-repo-url>
cd CourseHub/course_platform

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install django==5.0.1
python manage.py migrate
python manage.py shell < seed_data.py    # optional: load demo data
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

### Demo Accounts (after seeding)

| Role       | Username    | Password   |
|------------|-------------|------------|
| Admin      | admin       | admin123   |
| Analyst    | analyst     | analyst123 |
| Instructor | prof_sharma | inst123    |
| Student    | student1    | stud123    |

### Configuration

Set `DJANGO_SECRET_KEY` as an environment variable for any non-local deployment.
The default key in the code is only for development.

## Author

**Isha Raut**
