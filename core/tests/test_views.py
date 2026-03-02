from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from core.models import Task


User = get_user_model()


class ViewTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(username="owner", password="pass1234")
        self.other_user = User.objects.create_user(username="other", password="pass1234")

    def test_task_list_requires_login(self):
        response = self.client.get(reverse("task_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_create_task_sets_owner(self):
        self.client.login(username="owner", password="pass1234")
        payload = {
            "title": "New Task",
            "description": "Details",
            "status": "todo",
        }
        response = self.client.post(reverse("create_task"), payload, follow=True)
        self.assertEqual(response.status_code, 200)
        task = Task.objects.get(title="New Task")
        self.assertEqual(task.owner, self.user)

    def test_task_detail_accessible_to_owner(self):
        task = Task.objects.create(
            title="Owned Task",
            description="desc",
            owner=self.user,
        )
        self.client.login(username="owner", password="pass1234")
        response = self.client.get(reverse("task_detail", args=[task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Owned Task")

    def test_update_task_changes_status(self):
        task = Task.objects.create(
            title="Update Me",
            description="desc",
            owner=self.user,
        )
        self.client.login(username="owner", password="pass1234")
        response = self.client.post(
            reverse("update_task", args=[task.pk]),
            {
                "title": "Update Me",
                "description": "desc",
                "status": "done",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.status, "done")

    def test_delete_task_requires_post(self):
        task = Task.objects.create(
            title="Delete Me",
            description="desc",
            owner=self.user,
        )
        self.client.login(username="owner", password="pass1234")
        response = self.client.get(reverse("delete_task", args=[task.pk]))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Task.objects.filter(pk=task.pk).exists())

    def test_delete_task_post_deletes(self):
        task = Task.objects.create(
            title="Delete Me",
            description="desc",
            owner=self.user,
        )
        self.client.login(username="owner", password="pass1234")
        response = self.client.post(reverse("delete_task", args=[task.pk]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_non_owner_cannot_delete_task(self):
        task = Task.objects.create(
            title="Keep Me",
            description="desc",
            owner=self.user,
        )
        self.client.login(username="other", password="pass1234")
        response = self.client.post(reverse("delete_task", args=[task.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Task.objects.filter(pk=task.pk).exists())

    def test_logout_requires_post(self):
        self.client.login(username="owner", password="pass1234")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 405)
        self.assertIsNotNone(self.client.session.get("_auth_user_id"))

    def test_logout_post_logs_user_out(self):
        self.client.login(username="owner", password="pass1234")
        response = self.client.post(reverse("logout"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(self.client.session.get("_auth_user_id"))
