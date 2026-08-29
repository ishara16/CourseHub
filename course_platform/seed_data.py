"""
Sample data script for CourseHub
Run: python manage.py shell < seed_data.py

Creates demo users and courses for testing.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_platform.settings')
django.setup()

from accounts.models import (
    Credentials, Admin, DataAnalyst, Instructor, Student,
    AdminCredential, AnalystCredential, InstructorCredential, StudentCredential
)
from courses.models import Course, Topics, Books, University, CourseBooks, Takes, Teaches, Partner


def create_sample_data():
    print("Creating sample data...")
    
    # Clear existing data in correct order (respect foreign keys)
    Takes.objects.all().delete()
    Teaches.objects.all().delete()
    Partner.objects.all().delete()
    CourseBooks.objects.all().delete()
    
    # Delete credential links
    StudentCredential.objects.all().delete()
    InstructorCredential.objects.all().delete()
    AdminCredential.objects.all().delete()
    AnalystCredential.objects.all().delete()
    
    # Delete users
    Student.objects.all().delete()
    Instructor.objects.all().delete()
    Admin.objects.all().delete()
    DataAnalyst.objects.all().delete()
    
    # Delete credentials
    Credentials.objects.all().delete()
    
    # Delete course-related data
    Course.objects.all().delete()
    Topics.objects.all().delete()
    Books.objects.all().delete()
    University.objects.all().delete()
    
    print("Cleared existing data")
    
    # Create Admin
    if not Credentials.objects.filter(username='admin').exists():
        cred = Credentials(username='admin', role='admin')
        cred.set_password('admin123')
        cred.save()
        admin = Admin.objects.create(name='System Admin')
        AdminCredential.objects.create(admin=admin, username=cred)
        print("Created admin user: admin / admin123")
    
    # Create Data Analyst
    if not Credentials.objects.filter(username='analyst').exists():
        cred = Credentials(username='analyst', role='analyst')
        cred.set_password('analyst123')
        cred.save()
        analyst = DataAnalyst.objects.create(name='Data Analyst')
        AnalystCredential.objects.create(analyst=analyst, username=cred)
        print("Created analyst user: analyst / analyst123")
    
    # Create Instructors
    instructors_data = [
        ('prof_sharma', 'Dr. Sharma', 'sharma@example.com', 'Ph.D. Computer Science', 'India'),
        ('prof_gupta', 'Dr. Gupta', 'gupta@example.com', 'Ph.D. Mathematics', 'India'),
        ('prof_smith', 'Dr. Smith', 'smith@example.com', 'Ph.D. Data Science', 'USA'),
        ('prof_jones', 'Dr. Jones', 'jones@example.com', 'Ph.D. Software Engineering', 'UK'),
    ]
    
    for username, name, email, qualifications, nationality in instructors_data:
        if not Credentials.objects.filter(username=username).exists():
            cred = Credentials(username=username, role='instructor')
            cred.set_password('inst123')
            cred.save()
            instructor = Instructor.objects.create(
                name=name, email_id=email, 
                qualifications=qualifications, nationality=nationality
            )
            InstructorCredential.objects.create(instructor=instructor, username=cred)
            print(f"Created instructor: {username} / inst123")
    
    # Create Students
    students_data = [
        ('student1', 'Rahul Kumar', 'rahul@example.com', 20, 'India', 'Beginner'),
        ('student2', 'Priya Singh', 'priya@example.com', 22, 'India', 'Intermediate'),
        ('student3', 'John Doe', 'john@example.com', 21, 'USA', 'Advanced'),
        ('student4', 'Amit Patel', 'amit@example.com', 23, 'India', 'Beginner'),
        ('student5', 'Sarah Wilson', 'sarah@example.com', 19, 'UK', 'Intermediate'),
    ]
    
    for i, (username, name, email, age, nationality, skill) in enumerate(students_data, 1):
        if not Credentials.objects.filter(username=username).exists():
            cred = Credentials(username=username, role='student')
            cred.set_password('stud123')
            cred.save()
            student = Student.objects.create(
                student_id=f'S{i:04d}',
                name=name, email_id=email, age=age,
                nationality=nationality, skill_level=skill
            )
            StudentCredential.objects.create(student=student, username=cred)
            print(f"Created student: {username} / stud123")
    
    # Create Topics
    topics_data = [
        ('Python', 'Programming'),
        ('Machine Learning', 'Data Science'),
        ('Web Development', 'Software Engineering'),
        ('Database Systems', 'Computer Science'),
        ('Statistics', 'Mathematics'),
    ]
    
    for name, field in topics_data:
        Topics.objects.get_or_create(name=name, defaults={'field': field})
    print("Created topics")
    
    # Create Books
    books_data = [
        ('978-0134685991', 'Effective Java', 'Joshua Bloch'),
        ('978-1491957660', 'Fluent Python', 'Luciano Ramalho'),
        ('978-1449373320', 'Data Science from Scratch', "Joel Grus"),
    ]
    
    for isbn, name, authors in books_data:
        Books.objects.get_or_create(isbn_code=isbn, defaults={'name': name, 'authors': authors})
    print("Created books")
    
    # Create Universities
    universities_data = [
        ('IIT Kharagpur', 'India'),
        ('Stanford University', 'USA'),
        ('MIT', 'USA'),
        ('Oxford University', 'UK'),
    ]
    
    for name, country in universities_data:
        University.objects.get_or_create(name=name, defaults={'country': country})
    print("Created universities")
    
    # Create Courses with SINGLE partner university
    courses_data = [
        ('Introduction to Python', '8 weeks', 'certificate', 2999.00, 0),  # IIT Kharagpur
        ('Machine Learning Fundamentals', '12 weeks', 'diploma', 9999.00, 1),  # Stanford
        ('Full Stack Web Development', '16 weeks', 'degree', 24999.00, 2),  # MIT
        ('Database Management Systems', '10 weeks', 'certificate', 4999.00, 0),  # IIT Kharagpur
        ('Data Science with Python', '14 weeks', 'diploma', 14999.00, 1),  # Stanford
    ]
    
    all_unis = list(University.objects.all())
    all_topics = list(Topics.objects.all())
    all_instructors = list(Instructor.objects.all())

    for i, (name, duration, program_type, price, uni_index) in enumerate(courses_data):
        try:
            course = Course.objects.get(name=name)
            print(f"Found existing course: {name}")
        except Course.DoesNotExist:
            course = Course.objects.create(
                name=name,
                duration=duration,
                program_type=program_type,
                price=price,
                videos='https://example.com/videos/' + name.lower().replace(' ', '-'),
                notes='Course notes and materials available after enrollment.'
            )
            print(f"Created course: {name}")
        
        # Link SINGLE university
        if all_unis:
            uni = all_unis[uni_index % len(all_unis)]
            Partner.objects.get_or_create(course=course, university=uni)
            print(f"  ✓ Partnered with {uni.name}")
            
        # Link topics
        if all_topics:
            t1 = all_topics[i % len(all_topics)]
            t2 = all_topics[(i + 1) % len(all_topics)]
            course.topics.add(t1, t2)
            print(f"  ✓ Added topics")
        
        # Assign 1-2 instructors per course
        if all_instructors:
            # First instructor
            instructor1 = all_instructors[i % len(all_instructors)]
            Teaches.objects.get_or_create(course=course, instructor=instructor1)
            
            # Second instructor (for some courses)
            if i % 2 == 0 and len(all_instructors) > 1:
                instructor2 = all_instructors[(i + 1) % len(all_instructors)]
                Teaches.objects.get_or_create(course=course, instructor=instructor2)
                print(f"  ✓ Assigned instructors: {instructor1.name}, {instructor2.name}")
            else:
                print(f"  ✓ Assigned instructor: {instructor1.name}")

    print("Created courses with partnerships")
    
    # Enroll some students
    students = list(Student.objects.all())
    courses = list(Course.objects.all())
    
    if students and courses:
        for i, student in enumerate(students):
            # Enroll each student in 2 courses
            for j in range(2):
                course = courses[(i + j) % len(courses)]
                Takes.objects.get_or_create(
                    course=course, student=student,
                    defaults={'evaluation': ((i + j) * 9) % 101}
                )
        print("Enrolled students in courses")
    
    print("\n=== Sample Data Created ===")
    print("\nLogin Credentials:")
    print("  Admin:      admin / admin123")
    print("  Analyst:    analyst / analyst123")
    print("  Instructor: prof_sharma / inst123")
    print("  Student:    student1 / stud123")


if __name__ == '__main__':
    create_sample_data()
else:
    # Also run when imported or piped to shell
    create_sample_data()