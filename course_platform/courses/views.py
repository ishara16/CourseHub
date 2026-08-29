from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Course, Takes, Teaches, Topics
from accounts.models import Student, Instructor, StudentCredential, InstructorCredential
from accounts.views import role_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


def course_list(request):
    """List all courses with search, program, and topic functionality"""
    if not request.session.get('user_id'):
        return redirect('login')
    
    query = request.GET.get('q', '')
    program_filter = request.GET.get('program', '')
    topic_filter = request.GET.get('topic', '') 
    
    courses = Course.objects.all()
    
    if query:
        courses = courses.filter(
            Q(name__icontains=query) | 
            Q(topics__name__icontains=query)
        ).distinct()
    
    if program_filter:
        courses = courses.filter(program_type=program_filter)

    if topic_filter:
        courses = courses.filter(topics=topic_filter).distinct()
    
    context = {
        'courses': courses,
        'all_topics': Topics.objects.all(),
        'query': query,
        'program_filter': program_filter,
        'topic_filter': topic_filter,        
        'role': request.session.get('role'),
        'user_name': request.session.get('user_name'),
    }
    return render(request, 'courses/course_list.html', context)


def course_detail(request, course_id):
    """View course details"""
    if not request.session.get('user_id'):
        return redirect('login')
    
    course = get_object_or_404(Course, course_id=course_id)
    instructors = Teaches.objects.filter(course=course).select_related('instructor')
    
    is_enrolled = False
    enrollment = None
    role = request.session.get('role')
    user_id = request.session.get('user_id')
    
    if role == 'student':
        try:
            student_cred = StudentCredential.objects.get(username=user_id)
            enrollment = Takes.objects.filter(student=student_cred.student, course=course).first()
            is_enrolled = enrollment is not None
        except StudentCredential.DoesNotExist:
            pass

    is_instructor_for_this_course = False
    if role == 'instructor':
        try:
            inst_cred = InstructorCredential.objects.get(username=user_id)
            is_instructor_for_this_course = Teaches.objects.filter(
                instructor=inst_cred.instructor, 
                course=course
            ).exists()
        except InstructorCredential.DoesNotExist:
            pass

    can_view_content = (role == 'admin') or \
                       (role == 'instructor' and is_instructor_for_this_course) or \
                       (role == 'student' and is_enrolled)
    
    context = {
        'course': course,
        'instructors': instructors,
        'is_enrolled': is_enrolled,
        'can_view_content': can_view_content,
        'enrollment': enrollment,
        'role': role,
        'user_name': request.session.get('user_name'),
    }
    return render(request, 'courses/course_detail.html', context)


def enroll_course(request, course_id):
    """Enroll student in a course (Student only)"""
    if not request.session.get('user_id'):
        return redirect('login')
    
    if request.session.get('role') != 'student':
        messages.error(request, 'Only students can enroll in courses.')
        return redirect('course_detail', course_id=course_id)
    
    course = get_object_or_404(Course, course_id=course_id)
    
    try:
        student_cred = StudentCredential.objects.get(username=request.session.get('user_id'))
        student = student_cred.student
        
        if Takes.objects.filter(student=student, course=course).exists():
            messages.warning(request, 'You are already enrolled in this course.')
        else:
            Takes.objects.create(student=student, course=course)
            messages.success(request, f'Successfully enrolled in {course.name}!')
    except StudentCredential.DoesNotExist:
        messages.error(request, 'Student account not found.')
    
    return redirect('course_detail', course_id=course_id)


def unenroll_course(request, course_id):
    """Unenroll student from a course"""
    if not request.session.get('user_id'):
        return redirect('login')
    
    if request.session.get('role') != 'student':
        messages.error(request, 'Only students can manage enrollments.')
        return redirect('course_detail', course_id=course_id)
    
    course = get_object_or_404(Course, course_id=course_id)
    
    try:
        student_cred = StudentCredential.objects.get(username=request.session.get('user_id'))
        enrollment = Takes.objects.filter(student=student_cred.student, course=course)
        if enrollment.exists():
            enrollment.delete()
            messages.success(request, f'Successfully unenrolled from {course.name}.')
        else:
            messages.warning(request, 'You are not enrolled in this course.')
    except StudentCredential.DoesNotExist:
        messages.error(request, 'Student account not found.')
    
    return redirect('course_detail', course_id=course_id)


def add_content(request, course_id):
    """Add/Edit content to a course (Instructor only)"""
    if not request.session.get('user_id'):
        return redirect('login')
    
    if request.session.get('role') != 'instructor':
        messages.error(request, 'Only instructors can add content.')
        return redirect('course_detail', course_id=course_id)
    
    course = get_object_or_404(Course, course_id=course_id)
    
    try:
        instructor_cred = InstructorCredential.objects.get(username=request.session.get('user_id'))
        if not Teaches.objects.filter(instructor=instructor_cred.instructor, course=course).exists():
            messages.error(request, 'You are not assigned to teach this course.')
            return redirect('course_detail', course_id=course_id)
    except InstructorCredential.DoesNotExist:
        messages.error(request, 'Instructor account not found.')
        return redirect('course_detail', course_id=course_id)
    
    if request.method == 'POST':
        videos = request.POST.get('videos', '')
        notes = request.POST.get('notes', '')
        
        course.videos = videos
        course.notes = notes
        course.save()
        
        messages.success(request, 'Course content updated successfully!')
        return redirect('course_detail', course_id=course_id)
    
    context = {
        'course': course,
        'role': request.session.get('role'),
        'user_name': request.session.get('user_name'),
    }
    return render(request, 'courses/add_content.html', context)


def my_courses(request):
    """View enrolled courses (for students) or assigned courses (for instructors)"""
    if not request.session.get('user_id'):
        return redirect('login')
    
    role = request.session.get('role')
    courses = []
    
    if role == 'student':
        try:
            student_cred = StudentCredential.objects.get(username=request.session.get('user_id'))
            enrollments = Takes.objects.filter(student=student_cred.student).select_related('course')
            courses = [(e.course, e.evaluation, e.enrolled_at) for e in enrollments]
        except StudentCredential.DoesNotExist:
            pass
    elif role == 'instructor':
        try:
            instructor_cred = InstructorCredential.objects.get(username=request.session.get('user_id'))
            teaches = Teaches.objects.filter(instructor=instructor_cred.instructor).select_related('course')
            courses = [(t.course, None, None) for t in teaches]
        except InstructorCredential.DoesNotExist:
            pass
    
    context = {
        'courses': courses,
        'role': role,
        'user_name': request.session.get('user_name'),
    }
    return render(request, 'courses/my_courses.html', context)