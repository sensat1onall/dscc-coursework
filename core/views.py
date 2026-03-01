from django import forms
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render

from .models import Comment, Task


# ---------- Task Form ----------
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "status", "category", "collaborators"]
        widgets = {
            "status": forms.Select(attrs={"class": "status-select"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 3})}


# ---------- Home ----------
def home(request):
    if request.user.is_authenticated:
        return redirect("task_list")
    return render(request, "home.html")


# ---------- Register ----------
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("task_list")
        messages.error(request, "Please correct the highlighted errors.")
    else:
        form = UserCreationForm()

    return render(request, "register.html", {"form": form})


# ---------- Login ----------
def login_view(request):
    if request.user.is_authenticated:
        return redirect("task_list")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("task_list")
        messages.error(request, "Invalid credentials. Try again.")
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})


# ---------- Task List ----------
@login_required
def task_list(request):
    tasks = (
        Task.objects.filter(owner=request.user)
        .select_related("category")
        .prefetch_related("collaborators")
        .order_by("-updated_at")
    )
    shared_tasks = (
        Task.objects.filter(collaborators=request.user)
        .select_related("category")
        .prefetch_related("collaborators", "owner")
        .order_by("-updated_at")
    )
    return render(
        request,
        "task_list.html",
        {"tasks": tasks, "shared_tasks": shared_tasks},
    )


# ---------- Task Detail ----------
@login_required
def task_detail(request, pk):
    task = get_object_or_404(
        Task.objects.select_related("category", "owner").prefetch_related("collaborators"),
        pk=pk,
    )
    if task.owner != request.user and request.user not in task.collaborators.all():
        messages.error(request, "You do not have access to this task.")
        return redirect("task_list")

    comments = task.comments.select_related("author")

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.task = task
            new_comment.author = request.user
            new_comment.save()
            messages.success(request, "Comment added.")
            return redirect("task_detail", pk=task.pk)
    else:
        comment_form = CommentForm()

    return render(
        request,
        "task_detail.html",
        {"task": task, "comments": comments, "comment_form": comment_form},
    )


# ---------- Create Task ----------
@login_required
def create_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user
            task.save()
            form.save_m2m()
            return redirect("task_list")
    else:
        form = TaskForm()

    return render(request, "task_form.html", {"form": form})


# ---------- Delete Task ----------
@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    task.delete()
    return redirect("task_list")


# ---------- Update Task ----------
@login_required
def update_task(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated.")
            return redirect("task_detail", pk=task.pk)
    else:
        form = TaskForm(instance=task)
    return render(request, "task_form.html", {"form": form, "task": task})


# ---------- Logout ----------
def logout_view(request):
    logout(request)
    return redirect("home")
