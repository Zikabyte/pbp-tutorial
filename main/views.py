from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required 
from django.views.decorators.http import require_POST 
from django.core.exceptions import PermissionDenied 

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience
from main.models import Project

import datetime


def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')

    context = {
        "name": "Mohammad Zidane Kurnianto",
        "npm": "2506584861",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Baik itu membangun kode, maupun merusak kode, saya mempelajari dari keduanya. Saya tertarik dengan segala hal software engineering ddan AI engineering. "
        ),
        "project_list": Project.objects.all()[:3],
        "last_login": last_login,
    }
    return render(request, "index.html", context)

# --------------------------------- Projects --------------------------------- #

PROJECT_SORT_OPTIONS = {"name", "-name", "category", "-category"}
EXPERIENCE_SORT_OPTIONS = {"title", "-title", "category", "-category"}


def show_projects(request):
    title_query = request.GET.get("title", "").strip()
    category_query = request.GET.get("category", "").strip()
    sort_query = request.GET.get("sort", "name").strip()
    if sort_query not in PROJECT_SORT_OPTIONS:
        sort_query = "name"
    starred_query = request.GET.get("starred") == "1" and request.user.is_authenticated

    context = {
        "name": "Mohammad Zidane Kurnianto",
        "title_query": title_query,
        "category_query": category_query,
        "sort_query": sort_query,
        "starred_query": starred_query,
        "category_choices": Project.PROJECT_CATEGORIES_CHOICES,
        "form": ProjectForm(),
    }
    return render(request, "project.html", context)

@login_required(login_url="/login/")
def create_project(request):
    if not request.user.has_perm("main.add_project"):
        raise PermissionDenied

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

@require_POST
def create_project_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan proyek."},
            status=403,
        )

    form = ProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        return JsonResponse(
            {"message": "Proyek berhasil ditambahkan.", "pk": str(project.id)},
            status=201,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

@login_required(login_url="/login/")
def update_project(request, project_id):
    if not request.user.has_perm("main.change_project"):
        raise PermissionDenied

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
    starred_only = request.GET.get("starred") == "1" and request.user.is_authenticated

    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(name__icontains=title_query)

    if category_query:
        projects = projects.filter(category=category_query)

    if starred_only:
        projects = projects.filter(starred_by=request.user)

    projects = projects.order_by(sort_query)

    data = []

    if request.user.is_superuser:
        for project in projects:
            starred_users = project.starred_by.all()
            is_starred = request.user in starred_users if request.user.is_authenticated else False
            starred_by_names = ", ".join([u.username for u in starred_users])

            data.append({
                "pk": str(project.id),
                "fields": {
                    "name": project.name,
                    "description": project.description,
                    "category": project.category,
                    "project_url": project.project_url,
                    "image_url": project.image_url,
                    "star_count": starred_users.count(),
                    "is_starred": is_starred,
                    "starred_by_names": starred_by_names,
                }
            })
    else:
        for project in projects:
            starred_users = project.starred_by.all()
            is_starred = request.user in starred_users if request.user.is_authenticated else False

            data.append({
                "pk": str(project.id),
                "fields": {
                    "name": project.name,
                    "description": project.description,
                    "category": project.category,
                    "project_url": project.project_url,
                    "image_url": project.image_url,
                    "star_count": starred_users.count(),
                    "is_starred": is_starred,
                }
            })
    return JsonResponse(data, safe=False)

@login_required(login_url="/login/")
def delete_project(request, project_id):
    if not request.user.has_perm("main.delete_project"):
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")
        return redirect("main:show_projects")

    return redirect("main:show_projects")

# -------------------------------- Experience -------------------------------- #

def show_experience(request):
    experiences = _filtered_experiences(request)
    title_query = request.GET.get("title", "").strip()
    category_query = request.GET.get("category", "").strip()
    sort_query = request.GET.get("sort", "title").strip()
    if sort_query not in EXPERIENCE_SORT_OPTIONS:
        sort_query = "title"
    starred_query = request.GET.get("starred") == "1" and request.user.is_authenticated

    context = {
        "name": "Mohammad Zidane Kurnianto",
        "experience_list": experiences,
        "title_query": title_query,
        "category_query": category_query,
        "sort_query": sort_query,
        "starred_query": starred_query,
        "category_choices": Experience.EXPERIENCE_CHOICES,
    }
    return render(request, "experience.html", context)

def _filtered_experiences(request):
    title_query = request.GET.get("title", "").strip()
    category_query = request.GET.get("category", "").strip()
    sort_query = request.GET.get("sort", "title").strip()
    if sort_query not in EXPERIENCE_SORT_OPTIONS:
        sort_query = "title"
    starred_only = request.GET.get("starred") == "1" and request.user.is_authenticated

    experiences = Experience.objects.all()

    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    if category_query:
        experiences = experiences.filter(category=category_query)

    if starred_only:
        experiences = experiences.filter(starred_by=request.user)

    return experiences.order_by(sort_query)

def get_experience_json(request):
    experiences = _filtered_experiences(request)

    data = []

    for experience in experiences:
        starred_users = experience.starred_by.all()
        is_starred = request.user in starred_users if request.user.is_authenticated else False

        fields = {
            "title": experience.title,
            "description": experience.description,
            "category": experience.category,
            "thumbnail": experience.thumbnail,
            "started_at": experience.started_at,
            "ended_at": experience.ended_at,
            "star_count": starred_users.count(),
            "is_starred": is_starred,
        }
        if request.user.is_superuser:
            fields["starred_by_names"] = ", ".join(u.username for u in starred_users)

        data.append({"pk": str(experience.id), "fields": fields})

    return JsonResponse(data, safe=False)

@login_required(login_url="/login/")
def create_experience(request):
    if not request.user.has_perm("main.add_experience"):
        raise PermissionDenied
    
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

@require_POST
def create_experience_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan proyek."},
            status=403,
        )

    form = ExperienceForm(request.POST)
    if form.is_valid():
        experience = form.save()
        return JsonResponse(
            {"message": "Experience berhasil ditambahkan.", "pk": str(experience.id)},
            status=201,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

@login_required(login_url="/login/")
def update_experience(request, experience_id):
    if not request.user.has_perm("main.change_experience"):
        raise PermissionDenied

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

@login_required(login_url="/login/")
def delete_experience(request, experience_id):
    if not request.user.has_perm("main.delete_experience"):
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience berhasil dihapus!")
        return redirect("main:show_experience")

    return redirect("main:show_experience")

# ------------------------------- Auth Feature ------------------------------- #
def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Mohammad Zidane Kurnianto",
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Mohammad Zidane Kurnianto",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response

# ----------------------------------- Misc ----------------------------------- #
@login_required(login_url="/login/")
def toggle_project_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        # Kalau akun ini sudah pernah memberi star, batalkan star-nya.
        # Kalau belum, tambahkan star.
        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)

    return redirect("main:show_projects")

@login_required(login_url="/login/")
def toggle_experience_star(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        # Kalau akun ini sudah pernah memberi star, batalkan star-nya.
        # Kalau belum, tambahkan star.
        if request.user in experience.starred_by.all():
            experience.starred_by.remove(request.user)
        else:
            experience.starred_by.add(request.user)

    return redirect("main:show_experience")