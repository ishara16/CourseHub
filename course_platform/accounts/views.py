from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count
from .models import (
    Credentials, Admin, DataAnalyst, Instructor, Student,
    AdminCredential, AnalystCredential, InstructorCredential, StudentCredential
)
from courses.models import Course, Takes, Teaches, University, Partner
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db import IntegrityError


def login_view(request):
    """Handle user login"""
    if request.session.get('user_id'):
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            credential = Credentials.objects.get(username=username)
            if credential.check_password(password):
                request.session['user_id'] = username
                request.session['role'] = credential.role
                
                user_name = get_user_name(username, credential.role)
                request.session['user_name'] = user_name
                
                messages.success(request, f'Welcome, {user_name}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid password')
        except Credentials.DoesNotExist:
            messages.error(request, 'Username not found')
    
    return render(request, 'accounts/login.html')


def signup_view(request):
    """Handle new user registration"""
    if request.session.get('user_id'):
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        role = request.POST.get('role', 'student')
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        
        if not username or not name:
            messages.error(request, 'Username and Name are required.')
            return render(request, 'accounts/signup.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/signup.html')
        
        if Credentials.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken. Please choose another.')
            return render(request, 'accounts/signup.html')
        
        if role not in ('student', 'instructor'):
            messages.error(request, 'Invalid role selected.')
            return render(request, 'accounts/signup.html')
        
        try:
            validate_password(password)
        except ValidationError as e:
            for msg in e.messages:
                messages.error(request, msg)
            return render(request, 'accounts/signup.html')
        
        cred = Credentials(username=username, role=role)
        cred.set_password(password)
        cred.save()
        
        if role == 'instructor':
            instructor = Instructor.objects.create(name=name, email_id=email)
            InstructorCredential.objects.create(instructor=instructor, username=cred)
        else:
            student_id = f"S{Student.objects.count() + 1:04d}"
            student = Student.objects.create(student_id=student_id, name=name, email_id=email)
            StudentCredential.objects.create(student=student, username=cred)
        
        messages.success(request, 'Account created successfully! Please log in.')
        return redirect('login')
    
    return render(request, 'accounts/signup.html')


def get_user_name(username, role):
    """Get the user's name based on their role"""
    try:
        if role == 'admin':
            cred = AdminCredential.objects.get(username=username)
            return cred.admin.name
        elif role == 'analyst':
            cred = AnalystCredential.objects.get(username=username)
            return cred.analyst.name
        elif role == 'instructor':
            cred = InstructorCredential.objects.get(username=username)
            return cred.instructor.name
        elif role == 'student':
            cred = StudentCredential.objects.get(username=username)
            return cred.student.name
    except Exception:
        pass
    return username


def logout_view(request):
    """Handle user logout"""
    request.session.flush()
    messages.info(request, 'You have been logged out.')
    return redirect('login')


def dashboard_view(request):
    """Role-based dashboard"""
    if not request.session.get('user_id'):
        return redirect('login')
    
    role = request.session.get('role')
    context = {
        'user_name': request.session.get('user_name'),
        'role': role,
    }
    
    if role == 'admin':
        return render(request, 'accounts/admin_dashboard.html', context)
    elif role == 'analyst':
        return render(request, 'accounts/analyst_dashboard.html', context)
    elif role == 'instructor':
        return render(request, 'accounts/instructor_dashboard.html', context)
    elif role == 'student':
        return render(request, 'accounts/student_dashboard.html', context)
    
    return redirect('login')


def role_required(roles):
    """Decorator to restrict views to certain roles"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.session.get('user_id'):
                return redirect('login')
            if request.session.get('role') not in roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def manage_courses(request):
    """Admin view to manage all courses"""
    if not request.session.get('user_id') or request.session.get('role') != 'admin':
        return redirect('dashboard')
    
    courses = Course.objects.annotate(
        student_count=Count('takes')
    ).prefetch_related('teaches_set__instructor')
    
    context = {
        'courses': courses,
        'role': request.session.get('role'),
        'user_name': request.session.get('user_name'),
    }
    return render(request, 'accounts/manage_courses.html', context)


def manage_course_detail(request, course_id):
    if not request.session.get('user_id') or request.session.get('role') != 'admin':
        return redirect('dashboard')
    
    course = get_object_or_404(Course, course_id=course_id)
    
    if request.method == 'POST' and 'update_university' in request.POST:
        new_university_id = request.POST.get('university_id')
        if new_university_id:
            Partner.objects.filter(course=course).delete()
            
            university = get_object_or_404(University, university_id=new_university_id)
            Partner.objects.create(course=course, university=university)
            
            messages.success(request, f'Partner university updated to {university.name}')
            return redirect('manage_course_detail', course_id=course_id)
    
    try:
        current_partner = Partner.objects.get(course=course)
        current_university = current_partner.university
    except Partner.DoesNotExist:
        current_university = None
    
    teaches = Teaches.objects.filter(course=course).select_related('instructor')
    takes = Takes.objects.filter(course=course).select_related('student')
    
    existing_instructor_ids = teaches.values_list('instructor_id', flat=True)
    existing_student_ids = takes.values_list('student_id', flat=True)
    
    available_instructors = Instructor.objects.exclude(instructor_id__in=existing_instructor_ids)
    available_students = Student.objects.exclude(student_id__in=existing_student_ids)
    
    all_universities = University.objects.all()
    
    context = {
        'course': course,
        'teaches': teaches,
        'takes': takes,
        'current_university': current_university,
        'all_universities': all_universities,
        'all_instructors': available_instructors,
        'all_students': available_students,
        'role': request.session.get('role'),
        'user_name': request.session.get('user_name'),
    }
    return render(request, 'accounts/manage_course_detail.html', context)


def add_instructor_to_course(request, course_id):
    """Add an instructor to a course"""
    if not request.session.get('user_id') or request.session.get('role') != 'admin':
        return redirect('dashboard')
    
    if request.method == 'POST':
        course = get_object_or_404(Course, course_id=course_id)
        instructor_id = request.POST.get('instructor_id')
        instructor = get_object_or_404(Instructor, instructor_id=instructor_id)
        
        if Teaches.objects.filter(course=course, instructor=instructor).exists():
            messages.warning(request, f'{instructor.name} is already assigned to this course.')
        else:
            Teaches.objects.create(course=course, instructor=instructor)
            messages.success(request, f'{instructor.name} has been added to {course.name}.')
    
    return redirect('manage_course_detail', course_id=course_id)


def remove_instructor_from_course(request, course_id, instructor_id):
    """Remove an instructor from a course"""
    if not request.session.get('user_id') or request.session.get('role') != 'admin':
        return redirect('dashboard')
    
    course = get_object_or_404(Course, course_id=course_id)
    instructor = get_object_or_404(Instructor, instructor_id=instructor_id)
    
    Teaches.objects.filter(course=course, instructor=instructor).delete()
    messages.success(request, f'{instructor.name} has been removed from {course.name}.')
    
    return redirect('manage_course_detail', course_id=course_id)


def add_student_to_course(request, course_id):
    """Add a student to a course"""
    if not request.session.get('user_id') or request.session.get('role') != 'admin':
        return redirect('dashboard')
    
    if request.method == 'POST':
        course = get_object_or_404(Course, course_id=course_id)
        student_id = request.POST.get('student_id')
        student = get_object_or_404(Student, student_id=student_id)
        
        if Takes.objects.filter(course=course, student=student).exists():
            messages.warning(request, f'{student.name} is already enrolled in this course.')
        else:
            Takes.objects.create(course=course, student=student)
            messages.success(request, f'{student.name} has been enrolled in {course.name}.')
    
    return redirect('manage_course_detail', course_id=course_id)


def remove_student_from_course(request, course_id, student_id):
    """Remove a student from a course"""
    if not request.session.get('user_id') or request.session.get('role') != 'admin':
        return redirect('dashboard')
    
    course = get_object_or_404(Course, course_id=course_id)
    student = get_object_or_404(Student, student_id=student_id)
    
    Takes.objects.filter(course=course, student=student).delete()
    messages.success(request, f'{student.name} has been removed from {course.name}.')
    
    return redirect('manage_course_detail', course_id=course_id)


def create_user(request):
    """Create a new user"""
    if not request.session.get('user_id') or request.session.get('role') != 'admin':
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        name = request.POST.get('name')
        email = request.POST.get('email', '')
        
        if Credentials.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('create_user')
        
        try:
            validate_password(password)
        except ValidationError as e:
            messages.error(request, e.messages[0])
            return redirect('create_user')

        cred = Credentials(username=username, role=role)
        cred.set_password(password)
        cred.save()
        
        if role == 'admin':
            admin = Admin.objects.create(name=name)
            AdminCredential.objects.create(admin=admin, username=cred)
        elif role == 'analyst':
            analyst = DataAnalyst.objects.create(name=name)
            AnalystCredential.objects.create(analyst=analyst, username=cred)
        elif role == 'instructor':
            instructor = Instructor.objects.create(name=name, email_id=email)
            InstructorCredential.objects.create(instructor=instructor, username=cred)
        elif role == 'student':
            student_id = f"S{Student.objects.count() + 1:04d}"
            student = Student.objects.create(student_id=student_id, name=name, email_id=email)
            StudentCredential.objects.create(student=student, username=cred)
        
        messages.success(request, f'User {username} created successfully!')
        return redirect('dashboard')
    
    context = {
        'role': request.session.get('role'),
        'user_name': request.session.get('user_name'),
    }
    return render(request, 'accounts/create_user.html', context)

def create_course(request):
    """Create a new course with assigned instructor(s) and one partner university"""
    if not request.session.get('user_id') or request.session.get('role') != 'admin':
        return redirect('dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        duration = request.POST.get('duration')
        program_type = request.POST.get('program_type')
        price = request.POST.get('price', 0)
        instructor_ids = request.POST.getlist('instructor_id') 
        university_id = request.POST.get('university_id') 
        
        if Course.objects.filter(name=name).exists():
            messages.error(request, f'A course with the name "{name}" already exists. Please choose a different name.')
            all_instructors = Instructor.objects.all()
            all_universities = University.objects.all()
            context = {
                'all_instructors': all_instructors,
                'all_universities': all_universities,
                'role': request.session.get('role'),
                'user_name': request.session.get('user_name'),
                'form_data': request.POST
            }
            return render(request, 'accounts/create_course.html', context)
        
        if not university_id:
            messages.error(request, 'Please select a partner university for this course.')
            all_instructors = Instructor.objects.all()
            all_universities = University.objects.all()
            context = {
                'all_instructors': all_instructors,
                'all_universities': all_universities,
                'role': request.session.get('role'),
                'user_name': request.session.get('user_name'),
                'form_data': request.POST
            }
            return render(request, 'accounts/create_course.html', context)
        
        if not instructor_ids:
            messages.error(request, 'Please select at least one instructor for this course.')
            all_instructors = Instructor.objects.all()
            all_universities = University.objects.all()
            context = {
                'all_instructors': all_instructors,
                'all_universities': all_universities,
                'role': request.session.get('role'),
                'user_name': request.session.get('user_name'),
                'form_data': request.POST
            }
            return render(request, 'accounts/create_course.html', context)
        
        new_course = Course.objects.create(
            name=name,
            duration=duration,
            program_type=program_type,
            price=price
        )
        
        instructor_names = []
        for instructor_id in instructor_ids:
            instructor = get_object_or_404(Instructor, instructor_id=instructor_id)
            Teaches.objects.create(course=new_course, instructor=instructor)
            instructor_names.append(instructor.name)
        
        university = get_object_or_404(University, university_id=university_id)
        Partner.objects.create(course=new_course, university=university)
        
        success_msg = f'Course "{name}" created successfully!'
        if instructor_names:
            success_msg += f' Instructors: {", ".join(instructor_names)}.'
        success_msg += f' Partner University: {university.name}.'
        
        messages.success(request, success_msg)
        return redirect('manage_courses')
    
    all_instructors = Instructor.objects.all()
    all_universities = University.objects.all()
    
    context = {
        'all_instructors': all_instructors,
        'all_universities': all_universities,
        'role': request.session.get('role'),
        'user_name': request.session.get('user_name'),
    }
    return render(request, 'accounts/create_course.html', context)

def delete_course(request, course_id):
    """Delete a course and all its relations"""
    if not request.session.get('user_id') or request.session.get('role') != 'admin':
        return redirect('dashboard')
    
    course = get_object_or_404(Course, course_id=course_id)
    name = course.name
    course.delete()
    
    messages.success(request, f'Course "{name}" has been permanently deleted.')
    return redirect('manage_courses')

def edit_course(request, course_id):
    """Admin: Edit course details"""
    if not request.session.get('user_id') or request.session.get('role') != 'admin':
        return redirect('dashboard')
        
    if request.method == 'POST':
        course = get_object_or_404(Course, course_id=course_id)
        course.name = request.POST.get('name')
        course.duration = request.POST.get('duration')
        course.price = request.POST.get('price')
        course.program_type = request.POST.get('program_type')
        course.save()
        messages.success(request, 'Course details updated successfully.')
        
    return redirect('manage_course_detail', course_id=course_id)

def manage_users(request):
    """Admin: List all users with promote/delete options"""
    if not request.session.get('user_id') or request.session.get('role') != 'admin':
        return redirect('dashboard')

    query = request.GET.get('q', '')
    users = Credentials.objects.all().order_by('role', 'username')

    if query:
        users = users.filter(username__icontains=query)

    user_list = []
    for u in users:
        real_name = get_user_name(u.username, u.role)
        user_list.append({
            'username': u.username,
            'role': u.role,
            'name': real_name,
            'is_admin': u.role == 'admin'
        })

    context = {
        'users': user_list,
        'query': query,
        'role': request.session.get('role'),
        'user_name': request.session.get('user_name'),
    }
    return render(request, 'accounts/manage_users.html', context)


def promote_to_admin(request, username):
    """Elevate a user's privileges to Admin"""
    if not request.session.get('user_id') or request.session.get('role') != 'admin':
        return redirect('dashboard')

    try:
        cred = Credentials.objects.get(username=username)
        
        if cred.role == 'admin':
            messages.info(request, f'User {username} is already an Admin.')
            return redirect('manage_users')

        current_name = get_user_name(cred.username, cred.role)

        new_admin = Admin.objects.create(name=current_name)
        
        AdminCredential.objects.create(admin=new_admin, username=cred)

        cred.role = 'admin'
        cred.save()

        messages.success(request, f'Successfully elevated {current_name} ({username}) to Admin!')

    except Credentials.DoesNotExist:
        messages.error(request, 'User not found.')
    except Exception as e:
        messages.error(request, f'Error promoting user: {str(e)}')

    return redirect('manage_users')
def profile_view(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    role = request.session.get('role')
    username = request.session.get('user_id')
    profile = None

    if role == 'student':
        profile = get_object_or_404(StudentCredential, username=username).student
    elif role == 'instructor':
        profile = get_object_or_404(InstructorCredential, username=username).instructor
    elif role == 'admin':
        profile = get_object_or_404(AdminCredential, username=username).admin
    elif role == 'analyst':
        profile = get_object_or_404(AnalystCredential, username=username).analyst

    return render(request, 'accounts/profile.html', {'profile': profile, 'role': role})

def edit_profile(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    role = request.session.get('role')
    username = request.session.get('user_id')
    
    if role == 'student':
        obj = get_object_or_404(StudentCredential, username=username).student
    elif role == 'instructor':
        obj = get_object_or_404(InstructorCredential, username=username).instructor
    elif role == 'admin':
        obj = get_object_or_404(AdminCredential, username=username).admin
    elif role == 'analyst':
        obj = get_object_or_404(AnalystCredential, username=username).analyst

    if request.method == 'POST':
        obj.name = request.POST.get('name')
        
        if role == 'student':
            obj.email_id = request.POST.get('email_id')
            obj.age = request.POST.get('age')
            obj.skill_level = request.POST.get('skill_level')
            obj.nationality = request.POST.get('nationality')
        elif role == 'instructor':
            obj.email_id = request.POST.get('email_id')
            obj.qualifications = request.POST.get('qualifications')
            
        obj.save()
        request.session['user_name'] = obj.name
        return redirect('profile')

    return render(request, 'accounts/edit_profile.html', {'profile': obj, 'role': role})

def delete_user(request, username):
    """Admin: Delete an Instructor or Analyst from the system"""
    if not request.session.get('user_id') or request.session.get('role') != 'admin':
        return redirect('dashboard')
    
    try:
        user_to_delete = get_object_or_404(Credentials, username=username)
        
        allowed_roles = ['instructor', 'analyst']
        
        if user_to_delete.role not in allowed_roles:
            messages.error(request, f"You cannot delete {user_to_delete.role} accounts via this interface.")
        else:
            user_to_delete.delete() 
            messages.success(request, f"User {username} has been permanently removed.")
            
    except Exception as e:
        messages.error(request, f"Error deleting user: {str(e)}")
    
    return redirect('manage_users')
