from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('<int:course_id>/unenroll/', views.unenroll_course, name='unenroll_course'),
    path('<int:course_id>/add-content/', views.add_content, name='add_content'),
    path('my-courses/', views.my_courses, name='my_courses'),
]
