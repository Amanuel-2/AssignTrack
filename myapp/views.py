from datetime import timezone
from django.shortcuts import redirect, render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from requests import Response
from .forms import CustomUserCreationForm

from rest_framework import generics
from rest_framework.views import APIView
from .models import Post,Group,Submission
from .serializers import PostSerializer,SubmissionSerializer
from .permissions import IsLecturer,IsStudent
from math import ceil
from rest_framework.permissions import IsAuthenticated
def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("profile")
    else:
        form = CustomUserCreationForm()
    return render(request, "myapp/register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("profile")
    else:
        form = AuthenticationForm()
    return render(request, "myapp/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def profile_view(request):
    return render(request, "myapp/profile.html")
 
@login_required
def dashboard_view(request):
    return render(request, 'myapp/dashboard.html')
    
class PostCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsLecturer]

    def perform_create(self, serializer):
        post = serializer.save()
        if post.group_type in ['manual', 'automatic'] and post.max_students_per_group:

            students = post.course.students.all()
            total_students = students.count()

            number_of_groups = ceil(total_students / post.max_students_per_group)

            groups = []

            for i in range(1, number_of_groups + 1):
                group = Group.objects.create(
                    post=post,
                    name=f"Group {i}"
                )
                groups.append(group)

            # Automatic assignment
            if post.group_type == 'automatic':
                group_index = 0

                for student in students:
                    groups[group_index].members.add(student)

                    if groups[group_index].members.count() >= post.max_students_per_group:
                        group_index += 1
class SubmissionCreateView(generics.CreateAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [IsStudent]

class JoinGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):

        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({"error": "Group not found"}, status=404)

        post = group.post

        # Only students can join
        if request.user.profile.role != 'student':
            return Response({"error": "Only students can join groups"}, status=403)

        # Check deadline
        if timezone.now() > post.deadline:
            return Response({"error": "Deadline passed"}, status=400)

        # Prevent joining if automatic
        if post.group_type == 'automatic':
            return Response({"error": "Automatic assignment enabled"}, status=400)

        # Check group capacity
        if group.members.count() >= post.max_students_per_group:
            return Response({"error": "Group is full"}, status=400)

        group.members.add(request.user)

        return Response({"message": "Joined successfully"})
        print(request.user)
        print(request.user.is_authenticated)
        print(request.user.profile.role)