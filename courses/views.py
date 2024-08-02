from datetime import datetime, timedelta
from django.http import HttpRequest
from payme.views import MerchantAPIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from payme.methods.generate_link import GeneratePayLink
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from .models import (
    Check,
    Course,
    Module,
    Lesson,
    Subject,
    Quiz,
    Answer,
    Question,
    Rating,
    CourseRating,
)
from .serializers import (
    CourseRatingModelSerializer,
    ModuleSerializer,
    SubjectSerializer,
    ModulePostSerializer,
    CheckModelSerializer,
    LessonPostSerializer,
    LessonModelSerializer,
    RatingModelSerializer,
    CourseCreateSerializer,
    LessonModuleSerializer,
    CourseModelAllSerializer,
    CourseModelOneSerializer,
    CourseForRatingSerializer,
)
from users.models import Order




def buy(check: Check):
    course = check.course
    user = check.author
    course.students.add(user)
    modules = Module.objects.filter(course=course)
    module = modules.first()
    module.students.add(user)
    course_rating = CourseRating.objects.create(author=user, course=course, score=0)
    module.save()
    course.save()


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
def order_course(request: HttpRequest):
    course_id = request.data.get("course")
    course = get_object_or_404(Course, pk=course_id)
    order = Order.objects.create(
        amount=course.price*100
    )
    return Response({
        "status": "success",
        "errors": {},
        "data": {
            "order_id": order.pk
        }
    })


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
def buy_course(request: HttpRequest):
    user = request.user
    order_id = request.data.get("order_id")
    course_id = request.data.get("course")
    order = Order.objects.filter(pk=order_id)
    if not order:
        return Response({
            "status": "error",
            "errors": {
                "order_id": "order not found",
            },
            "data": {}
        })
    order = order.first()
    course = get_object_or_404(Course, pk=course_id)
    check = Check.objects.filter(order=order)
    if check:
        return Response({
            "status": "error",
            "errors": {
                "order_id": "order duplicated."
            },
            "data": {}
        })
    check = Check.objects.create(
        author=user,
        course=course,
        order=order,
        status="0",
    )
    return Response({
        "status": "success",
        "errors": {},
        "data": {
            "link": GeneratePayLink(order_id=order.pk, amount=order.amount).generate_link()
        }
    })


class PaymentCallBackApiView(MerchantAPIView):
    def create_transaction(self, order_id, action) -> None:
        print("order_id:", order_id, "action:", action)

    def perform_transaction(self, order_id, action) -> None:
        order = Order.objects.filter(pk=order_id)
        if order:
            order = order.first()
            check = Check.objects.filter(order=order)
            if check:
                check = check.first()
                check.status = 1
                check.save()
                buy(check=check)
        print("To'landi", "order_id:", order_id, "action:", action)


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
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
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
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
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
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
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
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
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
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
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
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
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
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
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
def end_lesson(request: HttpRequest):
    lesson_id = request.data.get("id")
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    is_last_lesson = Lesson.objects.filter(module=lesson.module).last()
    if lesson.pk == is_last_lesson.pk:
        modules = Module.objects.filter(course=lesson.module.course)
        next_module = None
        for i in modules:
            if i.pk == lesson.module.pk:
                try:
                    next_module = Module.objects.get(pk=int(i.pk)+1)
                    next_module.students.add(request.user)
                except:
                    pass
    lesson.finishers.add(request.user)
    return Response({
        "status": "success",
        "errors": {},
        "data": {}
    })


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
def create_course(request: HttpRequest):
    course_serializer = CourseCreateSerializer(Course, data=request.data, context={"request": request})
    if course_serializer.is_valid():
        c = course_serializer.create(course_serializer.validated_data)
        return Response({
            "status": "success",
            "errors": {},
            "data": {
                "id": c.pk
            }
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
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
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
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
def my_courses(request: HttpRequest):
    courses = []
    for course in Course.objects.all():
        print(request.user in course.students.all())
        image = course.author.image
        if image:
            image = image.url
        else:
            image = None
        if request.user in course.students.all():
            courses.append({
                "id": course.pk,
                "name": course.name,
                "percentage": course.percentage(request.user),
                "author": {
                    "id": course.author.pk,
                    "username": course.author.username,
                    "first_name": course.author.first_name,
                    "last_name": course.author.last_name,
                    "middle_name": course.author.middle_name,
                    "image": image,
                }
            })
    return Response({
        "status": "success",
        "errors": {},
        "data": {
            "courses": courses
        }
    })


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
def add_lesson(request: HttpRequest, course_id: int, module_id: int):
    course = get_object_or_404(Course, pk=course_id)
    module = get_object_or_404(Module, pk=module_id)
    lesson = LessonPostSerializer(Lesson, data=request.data, context={"module": module})
    if lesson.is_valid():
        l = lesson.create(lesson.validated_data)
        previous = Lesson.objects.filter(pk=request.data.get("previous"))
        if previous:
            previous = previous.first()
            previous.next = l
            previous.save()
    else:
        print(lesson.errors)
    return Response({
        "status": "success",
        "errors": {},
        "data": {}
    })


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
def edit_lesson(request: HttpRequest, course_id: int, module_id: int, lesson_id: int):
    course = get_object_or_404(Course, pk=course_id)
    module = get_object_or_404(Module, pk=module_id)
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    lesson = LessonPostSerializer(lesson, data=request.data, context={"module": module})
    if lesson.is_valid():
        lesson.save()
    else:
        print(lesson.errors)
    return Response({
        "status": "success",
        "errors": {},
        "data": {}
    })

@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
def add_module(request: HttpRequest, course_id: int):
    course = get_object_or_404(Course, pk=course_id)
    data = request.data.dict()
    data["course"] = course.pk
    module = ModulePostSerializer(Module, data=data)
    if module.is_valid():
        module.create(module.validated_data)
    else:
        print(module.errors)
    return Response({
        "status": "success",
        "errors": {},
        "data": {}
    })


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
def checks(request: HttpRequest):
    user = request.user
    checks_obj = Check.objects.filter(author=user)
    checks = CheckModelSerializer(checks_obj, many=True)
    return Response({
        "status": "success",
        "errors": {},
        "data": {
            "checks": checks.data,
        },
    })


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
def create_test(request: HttpRequest, course_id: int, module_id: int):
    course = get_object_or_404(Course, pk=course_id)
    module = get_object_or_404(Module, pk=module_id)
    quiz = Quiz.objects.create(
        name=request.data.get("quiz").get("name"),
        passing_score=70
    )
    for q in request.data.get("quiz").get("questions"):
        question = Question.objects.create(
            question=q.get("question"),
            type=q.get("type"),
            score=5
        )
        if q.get("type") == "writable":
            a = Answer.objects.create(
                value_1=q.get("answer_1").get("value_1"),
                is_correct=True
            )
            question.answers.add(a)
            question.save()
        else:
            if q.get("type") == "one_select" or q.get("type") == "many_select":
                a1 = Answer.objects.create(
                    value_1=q.get("answer_1").get("value_1"),
                    is_correct=q.get("answer_1").get("is_correct"),
                )
                a2 = Answer.objects.create(
                    value_1=q.get("answer_2").get("value_1"),
                    is_correct=q.get("answer_2").get("is_correct"),
                )
                a3 = Answer.objects.create(
                    value_1=q.get("answer_3").get("value_1"),
                    is_correct=q.get("answer_3").get("is_correct"),
                )
                a4 = Answer.objects.create(
                    value_1=q.get("answer_4").get("value_1"),
                    is_correct=q.get("answer_4").get("is_correct"),
                )
                question.answers.add(a1)
                question.answers.add(a2)
                question.answers.add(a3)
                question.answers.add(a4)
                question.save()
            elif q.get("type") == "matchable":
                a1 = Answer.objects.create(
                    value_1=q.get("answer_1").get("value_1"),
                    value_2=q.get("answer_1").get("value_2"),
                    is_correct=q.get("answer_1").get("is_correct"),
                )
                a2 = Answer.objects.create(
                    value_1=q.get("answer_2").get("value_1"),
                    value_2=q.get("answer_2").get("value_2"),
                    is_correct=q.get("answer_2").get("is_correct"),
                )
                a3 = Answer.objects.create(
                    value_1=q.get("answer_2").get("value_1"),
                    value_2=q.get("answer_3").get("value_2"),
                    is_correct=q.get("answer_3").get("is_correct"),
                )
                a4 = Answer.objects.create(
                    value_1=q.get("answer_4").get("value_1"),
                    value_2=q.get("answer_4").get("value_2"),
                    is_correct=q.get("answer_4").get("is_correct"),
                )
                question.answers.add(a1)
                question.answers.add(a2)
                question.answers.add(a3)
                question.answers.add(a4)
                question.save()
        quiz.questions.add(question)
        quiz.save()
    last_lesson = Lesson.objects.filter(module=module.pk)
    if last_lesson:
        last_lesson = last_lesson.last()
        lesson = Lesson.objects.create(
            name=request.data.get("quiz").get("name"),
            module=module,
            type="quiz",
            quiz=quiz
        )
        lesson.previous = last_lesson
        lesson.save()
        last_lesson.next = lesson
        last_lesson.save()
    return Response({
        "status": "success",
        "errors": {},
        "data": {},
    })



@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
def billing_reports(request: HttpRequest):
    reports_obj = Check.objects.filter(author=request.user)
    reports = CheckModelSerializer(reports_obj, many=True)
    return Response({
        "status": "success",
        "errors": {},
        "data": reports.data,
    })


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
def rate(request: HttpRequest):
    course_id = request.data.get("course") or 0
    module_id = request.data.get("module") or 0
    lesson_id = request.data.get("lesson") or 0
    score = request.data.get("score")
    percent = request.data.get("percent")
    course = Course.objects.get(pk=course_id)
    module = Module.objects.get(pk=module_id)
    lesson = Lesson.objects.get(pk=lesson_id)
    course_rating = CourseRating.objects.filter(author=request.user, course=course).first()
    course_rating.score += score
    course_rating.save()
    rating = Rating.objects.create(
        author=request.user,
        course=course,
        module=module,
        lesson=lesson,
        score=score,
        percent=percent
    )
    return Response({
        "status": "success",
        "errors": {},
        "data": {
            "message": "Saved!"
        }
    })


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
def rates(request: HttpRequest):
    ratings_obj = Rating.objects.filter(author=request.user)
    ratings = RatingModelSerializer(ratings_obj, many=True)
    return Response({
        "status": "success",
        "errors": {},
        "data": {
            "ratings": ratings.data
        }
    })



@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
def ratings(request: HttpRequest):
    course_id = request.data.get("course")
    type = request.data.get("type") or "monthly"
    course = Course.objects.get(pk=course_id)
    now = datetime.now()
    now_as_str = now.strftime("%Y-%m-%d")
    ratings_obj = CourseRating.objects.filter(course=course, created=now)
    if type == "monthly":
        one_month_ago = now - timedelta(days=30)
        one_month_ago_as_str = one_month_ago.strftime("%Y-%m-%d")
        ratings_obj = CourseRating.objects.filter(course=course, created__range=[one_month_ago_as_str, now_as_str])
    elif type == "weekly":
        one_week_ago = now - timedelta(days=7)
        one_week_ago_as_str = one_week_ago.strftime("%Y-%m-%d")
        ratings_obj = CourseRating.objects.filter(course=course, created__range=[one_week_ago_as_str, now_as_str])
    else:
        ratings_obj = Rating.objects.filter(course=course, created__day=now.day)
    ratings = CourseRatingModelSerializer(ratings_obj, many=True)
    return Response({
        "status": "success",
        "errors": {},
        "data": {
            "ratings": ratings.data
        },
    })


# api
@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated])
@authentication_classes(authentication_classes=[TokenAuthentication])
def get_courses_for_rating(request: HttpRequest):
    courses_obj = Course.objects.all()
    courses = CourseForRatingSerializer(courses_obj, many=True)
    return Response({
        "status": "success",
        "errors": {},
        "data": {
            "courses": courses.data
        }
    })