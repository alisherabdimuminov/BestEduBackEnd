from rest_framework import serializers

from .models import (
    Course,
    Module,
    Lesson,
    Quiz,
    Question,
    Answer,
    Subject,
    Check,
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
    
    is_open = serializers.SerializerMethodField("get_user")

    class Meta:
        model = Course
        fields = (
            "id", "name", "author_", "image", 
            "subject_", "description", "price", 
            "feedback", "count_modules", "count_students", "count_lessons", "length", "is_open"
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
    
    is_open = serializers.SerializerMethodField("get_user")
    students = UserSerializer(User, many=True)
    feedbackers = UserSerializer(User, many=True)
    modules = ModuleSerializer(Module, many=True)
    class Meta:
        model = Course
        fields = (
            "name", "author_", "image", "subject_", 
            "description", "price", "feedback", 
            "count_modules", "count_students", "students", "count_lessons", "length", "feedbackers",
            "modules", "is_open",
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
    class Meta:
        model = Lesson
        fields = ("name", "module", "video", "duration", "resource", "type", "previous")


class ModulePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ("name", "course", "required")


class OrderModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "amount", )

    
class CheckModelSerializer(serializers.ModelSerializer):
    author = UserSerializer(User, many=False)
    order = OrderModelSerializer(Order, many=False)
    class Meta:
        model = Check
        fields = ("author", "course", "order", "status", "created", )
