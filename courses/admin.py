from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import (
    Course, 
    Module, 
    Lesson, 
    Subject,
    Answer,
    Question,
    Quiz,
)


@admin.register(Course)
class CourseModelAdmin(ModelAdmin):
    list_display = ["name", "subject", "author"]


@admin.register(Module)
class ModuleModelAdmin(ModelAdmin):
    list_display = ["name", "course", "video_length"]


@admin.register(Lesson)
class LessonModelAdmin(ModelAdmin):
    list_display = ["name", "module"]


@admin.register(Subject)
class SubjectModelAdmin(ModelAdmin):
    list_display = ["name"]


@admin.register(Quiz)
class QuizModelAdmin(ModelAdmin):
    list_display = ["name", "count_questions"]


@admin.register(Question)
class QuestionModelAdmin(ModelAdmin):
    list_display = ["question", "type"]


@admin.register(Answer)
class AnswerModelAdmin(ModelAdmin):
    list_display = ["value_1", "value_2", "is_correct"]
