from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('lecturer', 'Lecturer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Post(models.Model):
    GROUP_TYPE_CHOICES = (
        ('individual', 'Individual'),
        ('manual', 'Manual Group'),
        ('automatic', 'Automatic Group'),
    )
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    deadline = models.DateTimeField(help_text="Submission deadline")

    # Teacher attached file (assignment PDF, DOC, etc.)
    attachment = models.FileField(upload_to='assignments/',blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    group_type = models.CharField(max_length=20, choices=GROUP_TYPE_CHOICES, default='individual')
    max_student_per_group = models.IntegerField(null=True,blank=True)

    def __str__(self):
        return self.title
    

class Group(models.Model): 
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name="groups")
    name = models.CharField(max_length=100)

    members = models.ManyToManyField(User,related_name="assignment_groups",blank=True)

    def __str__(self):
        return f"{self.name} - {self.post.title}"
    

class Submission(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="submissions")
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.post.title}"

class course(models.Model):
    name = models.CharField(max_length=200)
    lecturer = models.ForeignKey(User,on_delete=models.CASCADE)

    student = models.ManyToManyField(User, related_name="courses")

    def __str__(self):
        return self.name