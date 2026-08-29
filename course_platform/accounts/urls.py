from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Admin management
    path('manage/', views.manage_courses, name='manage_courses'),
    path('manage/<int:course_id>/', views.manage_course_detail, name='manage_course_detail'),
    path('manage/<int:course_id>/add-instructor/', views.add_instructor_to_course, name='add_instructor_to_course'),
    path('manage/<int:course_id>/remove-instructor/<int:instructor_id>/', views.remove_instructor_from_course, name='remove_instructor_from_course'),
    path('manage/<int:course_id>/add-student/', views.add_student_to_course, name='add_student_to_course'),
    path('manage/<int:course_id>/remove-student/<str:student_id>/', views.remove_student_from_course, name='remove_student_from_course'),
    path('create-user/', views.create_user, name='create_user'),
    path('create-course/', views.create_course, name='create_course'),
    path('manage/course/<int:course_id>/delete/', views.delete_course, name='delete_course'),
    path('manage/course/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('manage/users/', views.manage_users, name='manage_users'),
    path('manage/users/<str:username>/promote/', views.promote_to_admin, name='promote_user'),
    path('manage/users/<str:username>/delete/', views.delete_user, name='delete_user'),

    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]
