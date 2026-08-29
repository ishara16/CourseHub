from django.urls import path
from . import views

urlpatterns = [
    path('statistics/', views.statistics_dashboard, name='statistics'),
    path('courses/', views.course_statistics, name='course_statistics'),
    path('demographics/', views.student_demographics, name='student_demographics'),
]
