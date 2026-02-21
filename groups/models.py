from django.db import models
from django.contrib.auth.models import User

class Group(models.Model): 
    post = models.ForeignKey("assignments.Post",on_delete=models.CASCADE,related_name="groups")
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(
        User,
        related_name="assignment_groups",
        blank=True,
        db_table="myapp_group_members",
    )

    class Meta:
        db_table = "myapp_group"

    def __str__(self):
        return f"{self.name} - {self.post.title}"
    
