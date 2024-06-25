from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from users.models import Order, User


LESSON_TYPE = (
    ("lesson", "Lesson"),
    ("quiz", "Quiz"),
)

QUESTION_TYPE = (
    ("one_select", "One select"),
    ("multi_select", "Multi select"),
    ("matchable", "Matchable"),
    ("writeable", "Writeable")
)

CHECK_STATUS_TYPE = (
    (0, "Kutilmoqda"),
    (1, "To'langan"),
    (-1, "Bekor qilingan"),
)


class Answer(models.Model):
    value_1 = models.TextField()
    value_2 = models.TextField(null=True, blank=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.value_1
    

class Question(models.Model):
    question = models.TextField()
    type = models.CharField(max_length=30, choices=QUESTION_TYPE)
    answers = models.ManyToManyField(Answer, related_name="question_answers")
    score = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return self.question
    
    def json(self) -> dict:
        answers = []
        for answer in self.answers.all():
            if self.type == "writeable":
                answers.append({
                    "value_1": answer.value_1,
                    "value_2": None,
                    "is_correct": True
                })
                break
            elif self.type == "one_select":
                correct_found = False
                if answer.is_correct and not correct_found:
                    answers.append({
                        "value_1": answer.value_1,
                        "value_2": None,
                        "is_correct": True
                    })
                    correct_found = True
                else:
                    answers.append({
                        "value_1": answer.value_1,
                        "value_2": None,
                        "is_correct": False
                    })
            elif self.type == "multi_select":
                answers.append({
                    "value_1": answer.value_1,
                    "value_2": None,
                    "is_correct": answer.is_correct
                })
            elif self.type == "matchable":
                answers.append({
                    "value_1": answer.value_1,
                    "value_2": answer.value_2,
                    "is_correct": True
                })
        return {
            "question": self.question,
            "type": self.type,
            "answers": answers
        }


class Quiz(models.Model):
    name = models.CharField(max_length=5000)
    questions = models.ManyToManyField(Question, related_name="quiz_qustions")
    passing_score = models.IntegerField(default=70, null=True, blank=True, validators=[MinValueValidator(50), MaxValueValidator(100)])

    def __str__(self):
        return self.name
    
    def count_questions(self) -> int:
        return self.questions.count()


class Subject(models.Model):
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class Course(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    image = models.ImageField(null=True, blank=True, upload_to="images/courses/")
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    price = models.IntegerField(default=0)
    feedback = models.FloatField(default=0)
    feedbackers = models.ManyToManyField(User, related_name="course_feedbackers", null=True, blank=True)
    students = models.ManyToManyField(User, related_name="course_students", null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def author_(self):
        image = self.image
        if image:
            image = self.image.url
        else:
            image = None
        return {
            "id": self.author.pk,
            "phone": self.author.username,
            "first_name": self.author.first_name,
            "last_name": self.author.last_name,
            "middle_name": self.author.middle_name,
            "image": image
        }
    
    def subject_(self):
        return self.subject.name
    
    def count_modules(self) -> int:
        return Module.objects.filter(course=self).count()
    
    def count_students(self) -> int:
        return self.students.count()
    
    def modules(self):
        return Module.objects.filter(course=self)
    
    def count_lessons(self):
        return Lesson.objects.filter(module__course=self).count()
    
    def percentage(self, user):
        count = 0
        for module in self.modules():
            count += module.finished_lessons(user=user)
        if self.count_lessons() == 0:
            return 0
        return count * 100 / self.count_lessons()
    
    def length(self):
        return Lesson.objects.filter(module__course=self).aggregate(models.Sum("duration")).get("duration__sum")


class Module(models.Model):
    name = models.CharField(max_length=500)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    required = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    students = models.ManyToManyField(User, related_name="module_students", null=True, blank=True)
    finishers = models.ManyToManyField(User, related_name="module_finishers", null=True, blank=True)

    def __str__(self) -> str:
        return self.name
    
    def count_students(self) -> int:
        return self.students.count()
    
    def count_finishers(self) -> int:
        return self.finishers.count()
    
    def count_lessons(self) -> int:
        return Lesson.objects.filter(module=self).count()
    
    def students_list(self):
        return self.students.all()
    
    def finishers_list(self):
        return self.finishers.all()
    
    def lessons(self):
        return Lesson.objects.filter(module=self)
    
    def finished_lessons(self, user: User):
        lessons = Lesson.objects.filter(module=self)
        count = 0
        for lesson in lessons:
            if user in lesson.finishers.all():
                count += 1
        return count
    
    def video_length(self) -> int:
        return Lesson.objects.filter(module=self).aggregate(duration=models.Sum("duration")).get("duration") or 0
    

class Lesson(models.Model):
    name = models.CharField(max_length=500)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    video = models.URLField(max_length=5000, null=True, blank=True)
    duration =  models.IntegerField(null=True, blank=True)
    resource = models.FileField(upload_to="files/lessons/", null=True, blank=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=30, choices=LESSON_TYPE)
    previous = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="previous_lesson")
    next = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="next_lesson")
    finishers = models.ManyToManyField(User, related_name="lesson_finishers", null=True, blank=True)

    def __str__(self):
        return self.name
    
    def is_quiz(self):
        return True if self.quiz else False
    
    def has_previous(self):
        return True if self.previous else False
    
    def has_next(self):
        return True if self.next else False
    
    def count_finishers(self) -> int:
        return self.finishers.count()
    
    def finishers_list(self):
        return self.finishers.all()
    
    def end_lesson(self, user: User):
        self.finishers.add(user)


class Check(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Module")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Buyurtma raqami")
    status = models.CharField(max_length=2, choices=CHECK_STATUS_TYPE, verbose_name="Holati")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.status
