from django.urls import path

from .views import (
    rate,
    rates,
    checks,
    ratings,
    buy_course,
    my_courses,
    end_lesson,
    add_module,
    add_lesson,
    create_test,
    edit_lesson,
    order_course,
    create_course,
    update_course,
    get_one_course,
    get_all_courses,
    billing_reports,
    get_all_subjects,
    get_module_lesson,
    get_course_module,
    get_module_lessons,
    get_course_modules,
    get_courses_for_rating,
    PaymentCallBackApiView,
)


urlpatterns = [
    # subjects
    path('subjects/', get_all_subjects, name="subjects"),

    # courses
    path('', get_all_courses, name="courses"),
    path('course/<int:id>/', get_one_course, name="course"),
    path('course/<int:course_id>/modules/', get_course_modules, name="modules"),
    path('course/<int:course_id>/modules/module/<int:module_id>/', get_course_module, name="module"),
    path('course/<int:course_id>/modules/module/<int:module_id>/lessons/', get_module_lessons, name="lessons"),
    path('course/<int:course_id>/modules/module/<int:module_id>/lessons/lesson/<int:lesson_id>/', get_module_lesson, name="lesson"),
    path('course/<int:course_id>/modules/module/<int:module_id>/lessons/lesson/<int:lesson_id>/edit/', edit_lesson, name="edit_lesson"),
    path('course/<int:course_id>/modules/add_module/', add_module, name="add_module"),
    path('course/<int:course_id>/modules/module/<int:module_id>/add_lesson/', add_lesson, name="add_lesson"),
    path('course/<int:course_id>/modules/module/<int:module_id>/add_test/', create_test, name="create_test"),

    path('create/', create_course, name="create_course"),
    path('course/<int:id>/update/', update_course, name="update_course"),
    path('end/', end_lesson, name="end_lesson"),
    path('my/', my_courses, name="my_courses"),

    path("buy/", buy_course, name="buy_course"),
    path("order/", order_course, name="order_course"),
    path("payments/merchant/", PaymentCallBackApiView.as_view(), name="payments"),
    path("checks/", checks, name="checks"),
    path("billing_reports/", billing_reports, name="billing_reports"),

    path("ratings/", ratings, name="ratings"),
    path("rate/", rate, name="rate"),

    path("for_rating/", get_courses_for_rating, name="get_courses_for_ratings"),
    path("rates/", rates, name="rates"),
]
