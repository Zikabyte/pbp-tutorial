from django.shortcuts import render

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
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Mohammad Zidane Kurnianto",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def show_project(request):
    context = {
        "name": "Mohammad Zidane Kurnianto",
        "project_list": Project.objects.all(),
    }
    return render(request, "project.html", context)