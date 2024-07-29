from rest_framework import serializers

from .models import (
    Course,
    CourseRating,
    Module,
    Lesson,
    Quiz,
    Question,
    Answer,
    Subject,
    Check,
    Rating,
)
from users.models import User, Order


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ("id", "name", )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "middle_name", "image", )


class QuestionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ("json", )


class QuizModelSerializer(serializers.ModelSerializer):
    questions = QuestionModelSerializer(Question.objects.all(), many=True)
    class Meta:
        model = Quiz
        fields = ("name", "questions", )



class LessonModuleSerializer(serializers.ModelSerializer):
    requires_context = True
    def check_open(self, obj):
        request = self.context.get("request")
        if request:
            if (obj.has_previous()):
                if request.user in obj.previous.finishers.all():
                    return True
                else:
                    return False
            else:
                return True
        return True
    
    is_open = serializers.SerializerMethodField("check_open")
    quiz = serializers.PrimaryKeyRelatedField(many=False, queryset=Lesson.objects.all())
    class Meta:
        model = Lesson
        fields = ("id", "name", "type", "duration", "quiz", "is_open")


class LessonModelSerializer(serializers.ModelSerializer):
    requires_context = True
    def check_open(self, obj):
        request = self.context.get("request")
        if request:
            if (obj.has_previous()):
                if request.user in obj.previous.finishers.all():
                    return True
                else:
                    return False
            else:
                return True
        return True
    
    is_open = serializers.SerializerMethodField("check_open")
    quiz = QuizModelSerializer(Quiz.objects.all(), many=False)
    previous = LessonModuleSerializer(Lesson.objects.all(), many=False)
    next = LessonModuleSerializer(Lesson.objects.all(), many=False)
    finishers = UserSerializer(User.objects.all(), many=True)
    class Meta:
        model = Lesson
        fields = ("id", "name", "type", "video", "duration", "resource", "quiz", "previous", "next", "finishers", "is_open")

class ModuleRequiredSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ("id", "name", )


class ModuleSerializer(serializers.ModelSerializer):
    requires_context = True
    def get_user(self, obj):
        request = self.context.get("request")
        if request:
            if request.user in obj.students.all():
                return True
            return False
        return False
    
    is_open = serializers.SerializerMethodField("get_user")
    # required = serializers.PrimaryKeyRelatedField(many=False, queryset=Module.objects.all())
    required = ModuleRequiredSerializer(Module.objects.all(), many=False)
    students = UserSerializer(User.objects.all(), many=True)
    finishers = UserSerializer(User.objects.all(), many=True)
    lessons = LessonModuleSerializer(Lesson.objects.all(), many=True)
    class Meta:
        model = Module
        fields = ("id", "name", "required", "video_length", "count_students", "count_finishers", "count_lessons", "students", "finishers", "lessons", "is_open")


class CourseModelAllSerializer(serializers.ModelSerializer):
    requires_context = True
    def get_user(self, obj):
        request = self.context.get("request")
        if request:
            if request.user in obj.students.all():
                return True
            return False
        return False
    
    def quizzes(self, obj):
        modules = Module.objects.filter(course=obj)
        count = 0
        for module in modules:
            count += module.count_quizzes()
        return count
    
    is_open = serializers.SerializerMethodField("get_user")
    count_quizzes = serializers.SerializerMethodField("quizzes")

    class Meta:
        model = Course
        fields = (
            "id", "name", "author_", "image", 
            "subject_", "description", "price", 
            "feedback", "count_modules", "count_students", "count_lessons", "length", "is_open",
            "count_quizzes",
        )

class CourseModelOneSerializer(serializers.ModelSerializer):
    requires_context = True
    def get_user(self, obj):
        request = self.context.get("request")
        if request:
            if request.user in obj.students.all():
                return True
            return False
        return False
    
    def quizzes(self, obj):
        modules = Module.objects.filter(course=obj)
        count = 0
        for module in modules:
            count += module.count_quizzes()
        return count
    
    is_open = serializers.SerializerMethodField("get_user")
    count_quizzes = serializers.SerializerMethodField("quizzes")
    students = UserSerializer(User, many=True)
    feedbackers = UserSerializer(User, many=True)
    modules = ModuleSerializer(Module, many=True)
    class Meta:
        model = Course
        fields = (
            "name", "author_", "image", "subject_", 
            "description", "price", "feedback", 
            "count_modules", "count_students", "students", "count_lessons", "length", "feedbackers",
            "modules", "is_open", "count_quizzes",
            )


class CourseCreateSerializer(serializers.ModelSerializer):
    requires_context = True
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    image = serializers.ImageField(required=False)

    def create(self, validated_data):
        print(validated_data)
        course = Course.objects.create(
            author=self.context.get("request").user,
            **validated_data
        )
        return course

    class Meta:
        model = Course
        fields = ("name", "image", "subject", "description", "price", "author")


class LessonPostSerializer(serializers.ModelSerializer):
    resource = serializers.FileField(required=False)
    def create(self, validated_data):
        module_id = self.context.get("module")
        print(module_id)
        module = Module.objects.get(pk=module_id.pk)
        last_lesson = Lesson.objects.filter(module=module.pk)
        if last_lesson:
            last_lesson = last_lesson.last()
            validated_data["module"] = module
            lesson = Lesson.objects.create(**validated_data)
            lesson.previous = last_lesson
            lesson.save()
            last_lesson.next = lesson
            last_lesson.save()
        else:
            lesson = Lesson.objects.create(**validated_data)
        return lesson
    class Meta:
        model = Lesson
        fields = ("name", "video", "duration", "resource", "type", "previous")


class ModulePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ("name", "course", "required")


class OrderModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "amount", )


class CourseModelSerializerForCheck(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("id", "name", "price", )

    
class CheckModelSerializer(serializers.ModelSerializer):
    author = UserSerializer(User, many=False)
    order = OrderModelSerializer(Order, many=False)
    course = CourseModelSerializerForCheck(Course, many=False)
    class Meta:
        model = Check
        fields = ("author", "course", "order", "status", "created", )


class RatingModelSerializer(serializers.ModelSerializer):
    course = CourseModelSerializerForCheck(Course, many=False)
    class Meta:
        model = Rating
        fields = ("course", "module", "lesson", "author", "score", "")


class CourseRatingModelSerializer(serializers.ModelSerializer):
    course = CourseModelSerializerForCheck(Course, many=False)
    author = UserSerializer(User, many=False)
    class Meta:
        model = CourseRating
        fields = ("author", "course", "score", )
