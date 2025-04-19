from django.db.models import Max, Min, Avg, Count
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse

from core.models import Course, CourseContent, CourseMember, User

# Create your views here.
def index(request):
    return HttpResponse('<h1>Selamat datang di Docker Simple LMS</h1>')

def testing(request):
    guru = User.objects.create_user(
        username = 'guru_1',
        password = 'guru1@emal.com',
        email = 'rahasia',
        first_name = 'Guru',
        last_name = 'Satu'
    )

    Course.objects.create(
        name = 'Docker Simple LMS',
        description = 'Docker Simple Learning Management System',
        price = 50000,
        teacher = guru
    )

    return HttpResponse('kosongan')

def allCourse(request):
    allCourse = Course.objects.all().select_related('teacher')
    result = []
    for course in allCourse:
        record = {'id': course.id, 'name': course.name,
                  'description': course.description,
                  'price': course.price,
                  'teacher': {
                      'id': course.teacher.id,
                      'username': course.teacher.username,
                      'email': course.teacher.email,
                      'fullname': f"{course.teacher.first_name} {course.teacher.last_name}"
                  }}
        result.append(record)
    return JsonResponse(result, safe=False)

def userProfile(request, user_id):
    user = User.objects.get(pk=user_id)
    courses = Course.objects.filter(teacher=user)
    data_resp = {'username': user.username, 'email': user.email, 'fullName': f"{user.first_name} {user.last_name}",
                 'courses': []}
    for course in courses:
        course_data = {
            'id': course.id,
            'name': course.name,
            'description': course.description,
            'price': course.price
        }
        data_resp['courses'].append(course_data)

    return JsonResponse(data_resp, safe=False)

def courseStats(request):
    courses = Course.objects.all()
    statistic = courses.aggregate(
        course_count=Count('*'),
        min_price=Min('price'),
        max_price=Max('price'),
        avg_price=Avg('price')
    )

    cheapest_list = Course.objects.filter(price=statistic['min_price'])
    expensive_list = Course.objects.filter(price=statistic['max_price'])
    popular_list = Course.objects.annotate(member_count=Count('coursemember')) \
                       .order_by('-member_count')[:3]
    unpopular_list = Course.objects.annotate(member_count=Count('coursemember')) \
                         .order_by('member_count')[:3]

    data_resp = {
        'course_count': statistic['course_count'],
        'min_price': statistic['min_price'],
        'max_price': statistic['max_price'],
        'avg_price': statistic['avg_price'],
        'cheapest': [course.name for course in cheapest_list],
        'expensive': [course.name for course in expensive_list],
        'popular': [course.name for course in popular_list],
        'unpopular': [course.name for course in unpopular_list],
    }

    return JsonResponse(data_resp, safe=False)

def userStats(request):
    # Annotasi jumlah course yang dibuat oleh tiap user
    users_with_courses = User.objects.annotate(course_count=Count('course'))
    users_with_course_count = users_with_courses.filter(course_count__gt=0).count()
    users_without_course_count = users_with_courses.filter(course_count=0).count()

    # Rata-rata jumlah course yang diikuti oleh satu user
    course_counts = User.objects.annotate(joined_courses=Count('coursemember'))
    avg_joined_courses = course_counts.aggregate(avg=Avg('joined_courses'))['avg']

    # User yang mengikuti course terbanyak
    most_active_user = course_counts.order_by('-joined_courses').first()
    most_active_username = most_active_user.username if most_active_user else None

    # List user yang tidak mengikuti course sama sekali
    users_without_courses = course_counts.filter(joined_courses=0).values_list('username', flat=True)

    data_resp = {
        'users_with_course': users_with_course_count,
        'users_without_course': users_without_course_count,
        'avg_joined_courses': avg_joined_courses,
        'most_active_user': most_active_username,
        'users_not_joining_any_course': list(users_without_courses),
    }

    return JsonResponse(data_resp, safe=False)

