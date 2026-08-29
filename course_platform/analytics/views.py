from django.shortcuts import render, redirect
from django.db.models import Count, Avg
from courses.models import Course, Takes, Teaches
from accounts.models import Student, Instructor


def course_statistics(request):
    """Course statistics dashboard for Data Analyst"""
    if not request.session.get('user_id'):
        return redirect('login')
    
    if request.session.get('role') != 'analyst':
        return redirect('dashboard')
    
    total_courses = Course.objects.count()
    total_students = Student.objects.count()
    total_instructors = Instructor.objects.count()
    total_enrollments = Takes.objects.count()
    
    popular_courses = Course.objects.annotate(
        enrollment_count=Count('takes')
    ).order_by('-enrollment_count')[:10]
    
    course_by_type = Course.objects.values('program_type').annotate(
        count=Count('course_id')
    ).order_by('-count')
    
    avg_evaluations = Takes.objects.values('course__name').annotate(
        avg_eval=Avg('evaluation')
    ).order_by('-avg_eval')[:10]
    
    context = {
        'user_name': request.session.get('user_name'),
        'role': request.session.get('role'),
        'total_courses': total_courses,
        'total_students': total_students,
        'total_instructors': total_instructors,
        'total_enrollments': total_enrollments,
        'popular_courses': popular_courses,
        'course_by_type': course_by_type,
        'avg_evaluations': avg_evaluations,
    }
    
    return render(request, 'analytics/course_statistics.html', context)


def statistics_dashboard(request):
    """Statistics dashboard for Data Analyst (comprehensive view with all data)"""
    if not request.session.get('user_id'):
        return redirect('login')
    
    if request.session.get('role') != 'analyst':
        return redirect('dashboard')
    
    total_courses = Course.objects.count()
    total_students = Student.objects.count()
    total_instructors = Instructor.objects.count()
    total_enrollments = Takes.objects.count()
    
    popular_courses = Course.objects.annotate(
        enrollment_count=Count('takes')
    ).order_by('-enrollment_count')[:10]
    
    course_by_type = Course.objects.values('program_type').annotate(
        count=Count('course_id')
    ).order_by('-count')
    
    avg_evaluations = Takes.objects.values('course__name').annotate(
        avg_eval=Avg('evaluation')
    ).order_by('-avg_eval')[:10]
    
    demographics_by_nationality = Student.objects.values('nationality').annotate(
        count=Count('student_id')
    ).order_by('-count')
    
    skill_distribution = Student.objects.values('skill_level').annotate(
        count=Count('student_id')
    ).order_by('-count')
    
    enrollment_stats = Student.objects.annotate(
        course_count=Count('takes')
    ).values('course_count').annotate(
        student_count=Count('student_id')
    ).order_by('course_count')
    
    context = {
        'user_name': request.session.get('user_name'),
        'role': request.session.get('role'),
        'total_courses': total_courses,
        'total_students': total_students,
        'total_instructors': total_instructors,
        'total_enrollments': total_enrollments,
        'popular_courses': popular_courses,
        'course_by_type': course_by_type,
        'avg_evaluations': avg_evaluations,
        'demographics_by_nationality': demographics_by_nationality,
        'skill_distribution': skill_distribution,
        'enrollment_stats': enrollment_stats,
    }
    
    return render(request, 'analytics/statistics.html', context)


def student_demographics(request):
    """Student demographics page for Data Analyst"""
    if not request.session.get('user_id'):
        return redirect('login')
    
    if request.session.get('role') != 'analyst':
        return redirect('dashboard')
    
    total_courses = Course.objects.count()
    total_students = Student.objects.count()
    total_instructors = Instructor.objects.count()
    total_enrollments = Takes.objects.count()
    
    demographics_by_nationality = Student.objects.values('nationality').annotate(
        count=Count('student_id')
    ).order_by('-count')
    
    skill_distribution = Student.objects.values('skill_level').annotate(
        count=Count('student_id')
    ).order_by('-count')
    
    enrollment_stats = Student.objects.annotate(
        course_count=Count('takes')
    ).values('course_count').annotate(
        student_count=Count('student_id')
    ).order_by('course_count')
    
    context = {
        'user_name': request.session.get('user_name'),
        'role': request.session.get('role'),
        'total_courses': total_courses,
        'total_students': total_students,
        'total_instructors': total_instructors,
        'total_enrollments': total_enrollments,
        'demographics_by_nationality': demographics_by_nationality,
        'skill_distribution': skill_distribution,
        'enrollment_stats': enrollment_stats,
    }
    
    return render(request, 'analytics/student_demographics.html', context)
