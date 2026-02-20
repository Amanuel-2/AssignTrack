from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Group, Post, Profile, Submission


class JoinGroupApiTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(username="student1", password="pass1234")
        Profile.objects.update_or_create(user=self.student, defaults={"role": "student"})

        self.other_student = User.objects.create_user(username="student2", password="pass1234")
        Profile.objects.update_or_create(user=self.other_student, defaults={"role": "student"})

        self.lecturer = User.objects.create_user(username="lecturer1", password="pass1234")
        Profile.objects.update_or_create(user=self.lecturer, defaults={"role": "lecturer"})

        self.post = Post.objects.create(
            author=self.lecturer,
            title="A1",
            content="Desc",
            deadline=timezone.now() + timedelta(days=1),
            group_type="manual",
            max_students_per_group=1,
        )
        self.group1 = Group.objects.create(post=self.post, name="Group 1")
        self.group2 = Group.objects.create(post=self.post, name="Group 2")

    def test_student_can_join_manual_group(self):
        self.client.login(username="student1", password="pass1234")
        url = reverse("join_group_api", kwargs={"group_id": self.group1.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], "Successfully joined group.")
        self.assertEqual(response.json()["member_count"], 1)
        self.assertTrue(self.group1.members.filter(id=self.student.id).exists())

    def test_student_cannot_join_second_group_same_assignment(self):
        self.group1.members.add(self.student)
        self.client.login(username="student1", password="pass1234")
        url = reverse("join_group_api", kwargs={"group_id": self.group2.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "You are already in a group.")

    def test_group_capacity_is_enforced(self):
        self.group1.members.add(self.other_student)
        self.client.login(username="student1", password="pass1234")
        url = reverse("join_group_api", kwargs={"group_id": self.group1.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Group is full.")


class AssignmentDetailTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(username="studentA", password="pass1234")
        Profile.objects.update_or_create(user=self.student, defaults={"role": "student"})

        self.lecturer = User.objects.create_user(username="lecturerA", password="pass1234")
        Profile.objects.update_or_create(user=self.lecturer, defaults={"role": "lecturer"})

        self.post = Post.objects.create(
            author=self.lecturer,
            title="Assignment A",
            content="Content A",
            deadline=timezone.now() + timedelta(days=1),
            group_type="manual",
            max_students_per_group=3,
        )
        self.group = Group.objects.create(post=self.post, name="Group A")

    def test_manual_assignment_requires_group_before_submission(self):
        self.client.login(username="studentA", password="pass1234")
        url = reverse("assignment_detail", kwargs={"post_id": self.post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["can_submit"])
        self.assertIsNone(response.context["submission"])

    def test_submission_status_shows_submitted_when_submission_exists(self):
        self.group.members.add(self.student)
        Submission.objects.create(
            post=self.post,
            group=self.group,
            student=self.student,
            file="submissions/test.txt",
        )

        self.client.login(username="studentA", password="pass1234")
        url = reverse("assignment_detail", kwargs={"post_id": self.post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["submission"])
        self.assertFalse(response.context["can_submit"])

    def test_assignment_detail_displays_course_and_instructor(self):
        course = self.post.course = self.post.course or None
        if course is None:
            from .models import Course

            course = Course.objects.create(name="Web Development", lecturer=self.lecturer)
            self.post.course = course
            self.post.save(update_fields=["course"])

        self.client.login(username="studentA", password="pass1234")
        url = reverse("assignment_detail", kwargs={"post_id": self.post.id})
        response = self.client.get(url)

        self.assertContains(response, "Web Development")
        self.assertContains(response, self.lecturer.username)

    def test_lecturer_cannot_submit_assignment_from_detail_page(self):
        self.client.login(username="lecturerA", password="pass1234")
        url = reverse("assignment_detail", kwargs={"post_id": self.post.id})
        response = self.client.post(url, data={}, follow=False)
        self.assertEqual(response.status_code, 403)


class InstructorPostCrudAndGroupingTests(TestCase):
    def setUp(self):
        self.lecturer1 = User.objects.create_user(username="lect1", password="pass1234")
        Profile.objects.update_or_create(user=self.lecturer1, defaults={"role": "lecturer"})
        self.lecturer2 = User.objects.create_user(username="lect2", password="pass1234")
        Profile.objects.update_or_create(user=self.lecturer2, defaults={"role": "lecturer"})

        for i in range(15):
            student = User.objects.create_user(username=f"student_{i}", password="pass1234")
            Profile.objects.update_or_create(user=student, defaults={"role": "student"})

    def test_manual_groups_created_from_registered_student_count(self):
        self.client.login(username="lect1", password="pass1234")
        response = self.client.post(
            "/api/assignments/create/",
            data={
                "title": "Manual Group Assignment",
                "content": "Details",
                "deadline": (timezone.now() + timedelta(days=2)).isoformat(),
                "group_type": "manual",
                "max_students_per_group": 5,
            },
        )
        self.assertEqual(response.status_code, 201)
        post_id = response.json()["id"]
        self.assertEqual(Group.objects.filter(post_id=post_id).count(), 3)

    def test_instructor_can_only_update_own_post(self):
        own_post = Post.objects.create(
            author=self.lecturer1,
            title="Own",
            content="X",
            deadline=timezone.now() + timedelta(days=1),
            group_type="individual",
        )
        other_post = Post.objects.create(
            author=self.lecturer2,
            title="Other",
            content="Y",
            deadline=timezone.now() + timedelta(days=1),
            group_type="individual",
        )

        self.client.login(username="lect1", password="pass1234")
        own_url = reverse("assignment_api_detail", kwargs={"pk": own_post.id})
        other_url = reverse("assignment_api_detail", kwargs={"pk": other_post.id})

        own_response = self.client.patch(
            own_url,
            data={"title": "Own Updated"},
            content_type="application/json",
        )
        other_response = self.client.patch(
            other_url,
            data={"title": "Should Not Update"},
            content_type="application/json",
        )

        self.assertEqual(own_response.status_code, 200)
        self.assertEqual(other_response.status_code, 404)

        own_post.refresh_from_db()
        other_post.refresh_from_db()
        self.assertEqual(own_post.title, "Own Updated")
        self.assertEqual(other_post.title, "Other")


class InstructorHtmlCrudTests(TestCase):
    def setUp(self):
        self.lecturer = User.objects.create_user(username="lect_html", password="pass1234")
        Profile.objects.update_or_create(user=self.lecturer, defaults={"role": "lecturer"})
        self.student = User.objects.create_user(username="stud_html", password="pass1234")
        Profile.objects.update_or_create(user=self.student, defaults={"role": "student"})
        self.post = Post.objects.create(
            author=self.lecturer,
            title="HTML CRUD Post",
            content="Body",
            deadline=timezone.now() + timedelta(days=1),
            group_type="individual",
        )

    def test_instructor_can_edit_own_assignment_page(self):
        self.client.login(username="lect_html", password="pass1234")
        url = reverse("assignment_edit", kwargs={"post_id": self.post.id})
        response = self.client.post(
            url,
            data={
                "title": "Updated HTML CRUD Post",
                "content": "Body Updated",
                "deadline": (timezone.now() + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M"),
                "group_type": "individual",
                "max_students_per_group": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated HTML CRUD Post")

    def test_student_cannot_access_instructor_edit_delete_pages(self):
        self.client.login(username="stud_html", password="pass1234")
        edit_url = reverse("assignment_edit", kwargs={"post_id": self.post.id})
        delete_url = reverse("assignment_delete", kwargs={"post_id": self.post.id})

        edit_response = self.client.get(edit_url)
        delete_response = self.client.get(delete_url)

        self.assertEqual(edit_response.status_code, 403)
        self.assertEqual(delete_response.status_code, 403)
