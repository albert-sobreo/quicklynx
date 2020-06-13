from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Account)
admin.site.register(Login)
admin.site.register(Student)
admin.site.register(Classroom)
admin.site.register(Professor)
admin.site.register(Post)
admin.site.register(Lecture)
admin.site.register(Event)
admin.site.register(Message)
admin.site.register(Quiz_Event)
admin.site.register(Quiz_Section)
admin.site.register(Quiz_Question)
admin.site.register(Quiz_Answer)
admin.site.register(Quiz_Choices)
admin.site.register(Student_Quiz_Event)
admin.site.register(Attendance)
admin.site.register(Attendance_This_Day)