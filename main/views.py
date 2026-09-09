from django.shortcuts import render

from main.models import Experience


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
        "name": "Burhan",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)