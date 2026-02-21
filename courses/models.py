from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    name = models.CharField(max_length=200)
    lecturer = models.ForeignKey(User,on_delete=models.CASCADE)

    student = models.ManyToManyField(User, related_name="courses")

    class Meta:
        db_table = "myapp_course"

    def __str__(self):
        return self.name
