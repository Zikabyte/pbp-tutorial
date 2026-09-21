from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience
from main.models import Project


def show_main(request):
    context = {
        "name": "Mohammad Zidane Kurnianto",
        "npm": "2506584861",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Baik itu membangun kode, maupun merusak kode, saya mempelajari dari keduanya. Saya tertarik dengan segala hal software engineering ddan AI engineering. "
        ),
        "project_list": Project.objects.all()[:3],
    }
    return render(request, "index.html", context)

# --------------------------------- Projects --------------------------------- #

PROJECT_SORT_OPTIONS = {"name", "-name", "category", "-category"}
EXPERIENCE_SORT_OPTIONS = {"title", "-title", "category", "-category"}


def show_projects(request):
    json_response = get_projects_json(request)

    projects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    projects = [project.object for project in projects]
    title_query = request.GET.get("title", "").strip()
    category_query = request.GET.get("category", "").strip()
    sort_query = request.GET.get("sort", "name").strip()
    if sort_query not in PROJECT_SORT_OPTIONS:
        sort_query = "name"

    context = {
        "name": "Mohammad Zidane Kurnianto",
        "project_list": projects,
        "title_query": title_query,
        "category_query": category_query,
        "sort_query": sort_query,
        "category_choices": Project.PROJECT_CATEGORIES_CHOICES,
    }
    return render(request, "project.html", context)

def create_project(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
        "name": "Mohammad Zidane Kurnianto",
        "form": form,
    }
    return render(request, "projects_form.html", context)

def update_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek berhasil diperbarui!")
        return redirect("main:show_projects")

    context = {
        "name": "Mohammad Zidane Kurnianto",
        "form": form,
        "project": project,
    }
    return render(request, "projects_form.html", context)

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    category_query = request.GET.get("category", "").strip()
    sort_query = request.GET.get("sort", "name").strip()
    if sort_query not in PROJECT_SORT_OPTIONS:
        sort_query = "name"

    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(name__icontains=title_query)

    if category_query:
        projects = projects.filter(category=category_query)

    projects = projects.order_by(sort_query)

    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")

def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")
        return redirect("main:show_projects")

    return redirect("main:show_projects")

# -------------------------------- Experience -------------------------------- #

def show_experience(request):
    json_response = get_experience_json(request)

    experiences = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    experiences = [experience.object for experience in experiences]
    title_query = request.GET.get("title", "").strip()
    category_query = request.GET.get("category", "").strip()
    sort_query = request.GET.get("sort", "title").strip()
    if sort_query not in EXPERIENCE_SORT_OPTIONS:
        sort_query = "title"

    context = {
        "name": "Mohammad Zidane Kurnianto",
        "experience_list": experiences,
        "title_query": title_query,
        "category_query": category_query,
        "sort_query": sort_query,
        "category_choices": Experience.EXPERIENCE_CHOICES,
    }
    return render(request, "experience.html", context)

def get_experience_json(request):
    title_query = request.GET.get("title", "").strip()
    category_query = request.GET.get("category", "").strip()
    sort_query = request.GET.get("sort", "title").strip()
    if sort_query not in EXPERIENCE_SORT_OPTIONS:
        sort_query = "title"

    experiences = Experience.objects.all()

    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    if category_query:
        experiences = experiences.filter(category=category_query)

    experiences = experiences.order_by(sort_query)

    projects_json = serializers.serialize("json", experiences)
    return HttpResponse(projects_json, content_type="application/json")

def create_experience(request):
    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience baru berhasil ditambahkan!")
        return redirect("main:show_experience")

    context = {
        "name": "Mohammad Zidane Kurnianto",
        "form": form,
    }
    return render(request, "experience_form.html", context)

def update_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman berhasil diperbarui!")
        return redirect("main:show_experience")

    context = {
        "name": "Mohammad Zidane Kurnianto",
        "form": form,
        "experience": experience,
    }
    return render(request, "experience_form.html", context)

def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience berhasil dihapus!")
        return redirect("main:show_experience")

    return redirect("main:show_experience")