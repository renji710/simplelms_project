from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Course, CourseMember
from django.core import serializers
from django.db.models import Count, Avg, Min, Max, F

def user_course_statistics(request):
    """
    Menghitung dan mengembalikan statistik user terkait course.
    """
    users_creating_courses_count = Course.objects.values('teacher').distinct().count()
    # users_creating_courses_count = User.objects.annotate(
    #     num_courses_taught=Count('courses_taught') # Menggunakan related_name='courses_taught' di model Course
    # ).filter(num_courses_taught__gt=0).count()

    total_users_count = User.objects.count()
    users_not_creating_courses_count = total_users_count - users_creating_courses_count

    users_with_enrollments = CourseMember.objects.values('user').distinct()
    num_users_with_enrollments = users_with_enrollments.count()
    total_enrollments = CourseMember.objects.count()

    avg_courses_per_enrolled_user = 0
    if num_users_with_enrollments > 0:
        avg_courses_per_enrolled_user = total_enrollments / num_users_with_enrollments
        avg_courses_per_enrolled_user = round(avg_courses_per_enrolled_user, 2)


    users_by_enrollment = User.objects.annotate(
        enrollment_count=Count('coursemember')
    ).filter(enrollment_count__gt=0).order_by('-enrollment_count')

    top_users_list = []
    max_enrollments = 0
    if users_by_enrollment.exists():
        max_enrollments = users_by_enrollment.first().enrollment_count
        top_users_queryset = users_by_enrollment.filter(enrollment_count=max_enrollments)
        for user in top_users_queryset:
            top_users_list.append({
                'id': user.id,
                'username': user.username,
                'enrollment_count': user.enrollment_count
            })

    users_not_enrolled_queryset = User.objects.annotate(
        enrollment_count=Count('coursemember')
    ).filter(enrollment_count=0).order_by('username') 

    users_not_enrolled_list = []
    for user in users_not_enrolled_queryset:
         users_not_enrolled_list.append({
             'id': user.id,
             'username': user.username
         })


    statistics = {
        'users_creating_courses': users_creating_courses_count,
        'users_not_creating_courses': users_not_creating_courses_count,
        'average_courses_per_enrolled_user': avg_courses_per_enrolled_user,
        'max_enrollments_count': max_enrollments,
        'users_with_most_enrollments': top_users_list,
        'users_not_enrolled_count': users_not_enrolled_queryset.count(),
        'users_not_enrolled_list': users_not_enrolled_list,
    }

    return JsonResponse(statistics)


def courseStat(request):
    """
    Menampilkan statistik untuk semua course.
    (Contoh dari PDF hal 15 untuk demo N+1 & Optimasi)
    """
    courses = Course.objects.select_related('teacher').annotate(
        member_count_annotated=Count('coursemember')
    ).all() 
    
    stats = Course.objects.aggregate( 
        max_price=Max('price'),
        min_price=Min('price'),
        avg_price=Avg('price')
    )
    
    result_list = []
    for course in courses: 
        teacher_name = course.teacher.get_full_name() or course.teacher.username 
        member_count = course.member_count_annotated 
        
        result_list.append({
            'id': course.id,
            'name': course.name,
            'price': course.price,
            'teacher': teacher_name, 
            'member_count': member_count 
        })
        
    response_data = {
        'course_count': courses.count(), 
        'overall_stats': stats,
        'course_details': result_list 
    }

    return JsonResponse(response_data, safe=False)