from django.db import models
from datetime import date
import os

# Create your models here.
category_choices = {
    ("STUDENT", "Student"),
    ("ADMIN", "Admin"),
    ("PROFESSOR", "Professor")
}

semester_choices = {
    ("FIRST", "1st Semester"),
    ("SECOND", "2nd Semeseter"),
    ("SUMMER", "Summer")
}


class Login(models.Model):
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=255)
    category = models.CharField(max_length=50)
    verification_string = models.CharField(max_length=10, blank=True, null=True)
    verified = models.BooleanField(blank=True, null=True)

    class Meta:
        db_table = 'login'

    def __str__(self):
        return self.email


class Account(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    school_id = models.CharField(max_length=50)
    propix = models.ImageField(upload_to='pictures', blank=True, null=True)
    login = models.ForeignKey(Login, on_delete=models.CASCADE)
    # add noti_isChecked
    #add msgs_isChecked

    class Meta:
        db_table = 'account'

    def __str__(self):
        return self.last_name + ", " + self.first_name


class Classroom(models.Model):
    room_name = models.CharField(max_length=50)
    time_start = models.TimeField(null=True)
    time_end = models.TimeField(null=True)
    days = models.CharField(max_length=10)
    date_start = models.DateField(null=True)
    date_end = models.DateField(null=True)
    year_start = models.CharField(max_length=4, null=True, blank=True)
    year_end = models.CharField(max_length=4, null=True, blank=True)
    semester = models.CharField(max_length=25, choices=semester_choices, default="1st Semester")
    headerpix = models.ImageField(upload_to="media", blank=True, null=True)
    invite_token = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = "Classroom"

    def __str__(self):
        return self.room_name + "S.Y. " + self.year_start + "-" + self.year_end + self.semester


class Post(models.Model):
    text = models.CharField(max_length=512, blank=True, null=True)
    date = models.DateTimeField()
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)

    class Meta:
        db_table = 'post'

    def __str__(self):
        return str(self.date)


class Professor(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True)
    classroom = models.ManyToManyField(Classroom, blank=True)
    upvoted_post = models.ManyToManyField(Post, blank=True, related_name='upvoted_post_prof')
    downvoted_post = models.ManyToManyField(Post, blank=True, related_name='downvoted_post_prof')

    class Meta:
        db_table = "professor"

    def __str__(self):
        return self.account.last_name + ", " + self.account.first_name


class Student(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True)
    classroom = models.ManyToManyField(Classroom, blank=True)
    upvoted_post = models.ManyToManyField(Post, blank=True, related_name='upvoted_post_stud')
    downvoted_post = models.ManyToManyField(Post, blank=True, related_name='downvoted_post_stud')

    class Meta:
        db_table = "student"

    def __str__(self):
        return self.account.last_name + ", " + self.account.first_name


class Event(models.Model):
    title = models.CharField(max_length=50)
    date = models.DateField()
    description = models.CharField(max_length=500, blank=True, null=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    color = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        db_table = 'event'

    def __str__(self):
        return self.title


class Lecture(models.Model):
    no = models.FloatField(null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    file_loc = models.FileField(upload_to='media', null=True, blank=True)
    date = models.DateTimeField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)

    def extension(self):
        name, extension = os.path.splitext(self.file_loc.name)
        return extension

    def __str__(self):
        return self.title


class Message(models.Model):
    message = models.CharField(max_length=512, null=True, blank=True)
    subject = models.CharField(max_length=140, null=True, blank=True)
    date = models.DateTimeField()
    message_from = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="message_from", blank=True, null=True)
    message_to = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="message_to", blank=True, null=True)

    class Meta:
        db_table = 'message'

    def __str__(self):
        return self.subject


class Quiz_Choices(models.Model):
    choice = models.CharField(max_length=1024)

    class Meta:
        db_table = 'quiz_choices'

    def __str__(self):
        return self.choice


class Quiz_Answer(models.Model):
    quiz_answer = models.CharField(max_length=128)

    class Meta:
        db_table = 'quiz_answer'

    def __str__(self):
        return str(self.quiz_answer)


class Quiz_Question(models.Model):
    question = models.CharField(max_length=1024)
    quiz_choices = models.ManyToManyField(Quiz_Choices, blank=True)
    quiz_answer = models.ForeignKey(Quiz_Answer, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = "quiz_question"

    def __str__(self):
        return self.question


class Quiz_Section(models.Model):
    quiz_type = models.CharField(max_length=256, null=True)
    instruction = models.CharField(max_length=512, null=True, blank=True)
    points_per_item = models.IntegerField(null=True)
    quiz_question = models.ManyToManyField(Quiz_Question, blank=True)

    class Meta:
        db_table = 'quiz_section'

    def __str__(self):
        return "Section " + str(self.pk)


class Quiz_Event(models.Model):
    quiz_name = models.CharField(max_length=256)
    date = models.DateTimeField(null=True)
    deadline = models.DateTimeField()
    classroom = models.ForeignKey(Classroom, null=True, blank=True, on_delete=models.CASCADE)
    quiz_section = models.ManyToManyField(Quiz_Section, blank=True)

    class Meta:
        db_table = 'quiz_event'

    def __str__(self):
        return self.quiz_name