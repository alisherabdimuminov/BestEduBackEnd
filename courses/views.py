from django.http import HttpRequest
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from .models import (
    Course,
    Module,
    Lesson,
    Quiz,
    Question,
    Answer,
    Subject
)
from .serializers import (
    ModuleSerializer,
    SubjectSerializer,
    LessonModelSerializer,
    CourseCreateSerializer,
    LessonModuleSerializer,
    CourseModelAllSerializer,
    CourseModelOneSerializer,
)


@api_view(http_method_names=["GET"])
@authentication_classes(authentication_classes=[TokenAuthentication])
@permission_classes(permission_classes=[IsAuthenticated])
def get_all_subjects(request: HttpRequest):
    subjects_queryset = Subject.objects.all()
    subjects = SubjectSerializer(subjects_queryset, many=True).data
    return Response({
        "status": "success",
        "errors": {},
        "data": {
            "subjects": subjects
        }
    })


@api_view(http_method_names=["GET"])
@authentication_classes(authentication_classes=[TokenAuthentication])
@permission_classes(permission_classes=[IsAuthenticated])
def get_all_courses(request: HttpRequest):
    name = request.GET.get("name") or ""
    subject = request.GET.get("subject") or 0
    courses_queryset = Course.objects.filter(name__contains=name)
    if subject != 0:
        courses_queryset = courses_queryset.filter(subject__id=subject)
    courses = CourseModelAllSerializer(courses_queryset, many=True, context={"request": request}).data
    return Response({
        "status": "success",
        "errors": {},
        "data": {
            "courses": courses
        }
    })


@api_view(http_method_names=["GET"])
@authentication_classes(authentication_classes=[TokenAuthentication])
@permission_classes(permission_classes=[IsAuthenticated])
def get_one_course(request, id):
    course_queryset = get_object_or_404(Course, pk=id)
    course = CourseModelOneSerializer(course_queryset, context={"request": request}).data
    return Response({
        "status": "success",
        "errors": {},
        "data": {
            "course": course
        }
    })


@api_view(http_method_names=["GET"])
@authentication_classes(authentication_classes=[TokenAuthentication])
@permission_classes(permission_classes=[IsAuthenticated])
def get_course_modules(request: HttpRequest, course_id: int):
    course = get_object_or_404(Course, pk=course_id)
    modules_queryset = Module.objects.filter(course=course)
    modules = ModuleSerializer(modules_queryset, many=True, context={"request": request}).data
    return Response({
        "status": "success",
        "errors": {},
        "data": {
            "course": {
                "id": course.pk,
                "name": course.name,
            },
            "modules": modules
        }
    })


@api_view(http_method_names=["GET"])
@authentication_classes(authentication_classes=[TokenAuthentication])
@permission_classes(permission_classes=[IsAuthenticated])
def get_course_module(request: HttpRequest, course_id: int, module_id):
    course = get_object_or_404(Course, pk=course_id)
    module_queryset = get_object_or_404(Module, pk=module_id)
    module = ModuleSerializer(module_queryset, many=False, context={"request": request}).data
    return Response({
        "status": "success",
        "errors": {},
        "data": {
            "course": {
                "id": course_id,
                "name": course.name
            },
            "module": module
        }
    })


@api_view(http_method_names=["GET"])
@authentication_classes(authentication_classes=[TokenAuthentication])
@permission_classes(permission_classes=[IsAuthenticated])
def get_module_lessons(request: HttpRequest, course_id: int, module_id: int):
    course = get_object_or_404(Course, pk=course_id)
    module_queryset = get_object_or_404(Module, pk=module_id)
    lessons_queryset = Lesson.objects.filter(module=module_queryset)
    lessons = LessonModuleSerializer(lessons_queryset, many=True, context={"request": request}).data
    return Response({
        "status": "success",
        "errors": {},
        "data": {
            "lessons": lessons
        }
    })


@api_view(http_method_names=["GET"])
@authentication_classes(authentication_classes=[TokenAuthentication])
@permission_classes(permission_classes=[IsAuthenticated])
def get_module_lesson(request: HttpRequest, course_id: int, module_id: int, lesson_id: int):
    course = get_object_or_404(Course, pk=course_id)
    module = get_object_or_404(Module, pk=module_id)
    lesson_queryset = get_object_or_404(Lesson, pk=lesson_id)
    lesson = LessonModelSerializer(lesson_queryset, many=False, context={"request": request}).data
    return Response({
        "status": "success",
        "errors": {},
        "data": {
            "lesson": lesson
        }
    })


@api_view(http_method_names=["POST"])
@authentication_classes(authentication_classes=[TokenAuthentication])
@permission_classes(permission_classes=[IsAuthenticated])
def end_lesson(request: HttpRequest):
    lesson_id = request.data.get("id")
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    lesson.finishers.add(request.user)
    return Response({
        "status": "success",
        "errors": {},
        "data": {}
    })


@api_view(http_method_names=["POST"])
@authentication_classes(authentication_classes=[TokenAuthentication])
@permission_classes(permission_classes=[IsAuthenticated])
def create_course(request: HttpRequest):
    course_serializer = CourseCreateSerializer(Course, data=request.data, context={"request": request})
    if course_serializer.is_valid():
        course_serializer.create(course_serializer.validated_data)
        return Response({
            "status": "success",
            "errors": {},
            "data": {}
        })
    else:
        errors = {}
        for error in course_serializer.errors:
            errors[error] = course_serializer.errors[error]
        return Response({
            "status": "error",
            "errors": errors,
            "data": {}
        })
    
@api_view(http_method_names=["POST"])
@authentication_classes(authentication_classes=[TokenAuthentication])
@permission_classes(permission_classes=[IsAuthenticated])
def update_course(request: HttpRequest, id):
    course = get_object_or_404(Course, pk=id)
    course_serializer = CourseCreateSerializer(course, data=request.data, context={"request": request})
    if course_serializer.is_valid():
        course_serializer.save()
        return Response({
            "status": "success",
            "errors": {},
            "data": {}
        })
    else:
        errors = {}
        for error in course_serializer.errors:
            errors[error] = course_serializer.errors[error]
        return Response({
            "status": "error",
            "errors": errors,
            "data": {}
        })
    
@api_view(http_method_names=["GET"])
@authentication_classes(authentication_classes=[TokenAuthentication])
@permission_classes(permission_classes=[IsAuthenticated])
def my_courses(request: HttpRequest):
    courses = []
    for course in Course.objects.all():
        print(request.user in course.students.all())
        if request.user in course.students.all():
            courses.append({
                "id": course.pk,
                "percentage": course.percentage(request.user)
            })
    return Response({
        "status": "success",
        "errors": {},
        "data": {
            "courses": courses
        }
    })
