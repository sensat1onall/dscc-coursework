from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import Category, Comment, Task


User = get_user_model()


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="owner", password="pass1234")
        self.collaborator = User.objects.create_user(
            username="collab",
            password="pass1234",
        )
        self.category = Category.objects.create(name="Work")

    def test_category_str(self):
        self.assertEqual(str(self.category), "Work")

    def test_task_defaults_and_relationships(self):
        task = Task.objects.create(
            title="Write report",
            description="Finish section",
            owner=self.user,
            category=self.category,
        )
        task.collaborators.add(self.collaborator)
        self.assertEqual(task.status, "todo")
        self.assertIn(self.collaborator, task.collaborators.all())
        self.assertEqual(str(task), "Write report")

    def test_comment_creation(self):
        task = Task.objects.create(
            title="Review code",
            description="Check PR",
            owner=self.user,
        )
        comment = Comment.objects.create(task=task, author=self.user, body="Looks good")
        self.assertEqual(str(comment), f"Comment by {self.user} on {task}")
        self.assertEqual(comment.task, task)
