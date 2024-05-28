from django.urls import path

from .views import (
    get_all_courses,
    get_one_course,
    get_all_subjects,
    get_course_module,
    get_course_modules,
    get_module_lessons,
    get_module_lesson,
    create_course,
    update_course,
    end_lesson,
    my_courses,
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

    path('create/', create_course, name="create_course"),
    path('course/<int:id>/update/', update_course, name="update_course"),
    path('end/', end_lesson, name="end_lesson"),
    path('my/', my_courses, name="my_courses"),
]
