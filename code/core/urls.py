from django.urls import path
from . import views 

app_name = 'core' 

urlpatterns = [
    path('statistics/', views.user_course_statistics, name='user_course_stats'),
    path('course-stats/', views.courseStat, name='course_stats_demo'),
]