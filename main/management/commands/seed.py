from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from main.models import Experience, Project

EDITOR_GROUP_NAME = "Editor"
EDITOR_PERMISSION_CODENAMES = ["change_project", "change_experience"]

EXPERIENCES = [
    {
        "title": "Asisten DDP-1",
        "description": (
            "Membantu mahasiswa memahami dasar pengembangan pemrograman "
            "menggunakan Python."
        ),
        "category": "part-time",
    },
    {
        "title": "Member of Mobile Development SIG RISTEK 2026",
        "description": (
            "Berperan dalam proyek-proyek pengembangan aplikasi seluler di dalam "
            "SIG Mobile Development, dengan fokus pada pembuatan dan pemeliharaan "
            "aplikasi Android/iOS."
        ),
        "category": "full-time",
    },
]

PROJECTS = [
    {
        "name": "FisioMate",
        "description": (
            "FisioMate adalah platform Remote Therapeutic Monitoring berbasis AI "
            "yang memantau latihan fisioterapi (home exercise program) mandiri "
            "secara real-time via kamera Smartphone. Sistem ini mendeteksi "
            "kebenaran bentuk gerakan dan menghitung repetisi pasien secara "
            "otomatis tanpa perangkat wearable, sekaligus menyediakan dashboard "
            "web bagi terapis untuk memantau kepatuhan serta progres pemulihan "
            "pasien dari jarak jauh."
        ),
        "image_url": "/static/img/project-fisiomate.jpg",
        "category": "ai-engineering",
        "project_url": "https://github.com/FisioMate",
    },
    {
        "name": "GARDA NLP",
        "description": (
            "GARDA NLP adalah sistem klasifikasi teks berbasis SetFit yang "
            "dikembangkan untuk mendeteksi indikasi predatory grooming secara "
            "dini pada percakapan digital melalui analisis konteks bahasa, guna "
            "membantu orang tua mengenali risiko tanpa harus memantau seluruh "
            "percakapan anak secara manual."
        ),
        "image_url": "/static/img/project-garda.jpg",
        "category": "ai-engineering",
        "project_url": "https://github.com/Zikabyte/garda-nlp",
    },
    {
        "name": "Zikapedia",
        "description": "Portfolio berbasis React yang saya buat saat semester 1.",
        "image_url": "/static/img/project-zikapedia.png",
        "category": "web-development",
        "project_url": "https://zikapedia.vercel.app/",
    },
    {
        "name": "Samudera",
        "description": (
            "Samudera adalah mobile app untuk memantau saham, berita pasar, dan "
            "data perusahaan secara real-time menggunakan Flutter dan "
            "AlphaVantage API."
        ),
        "image_url": "/static/img/project-samudera.png",
        "category": "mobile-development",
        "project_url": "https://github.com/Zikabyte/samudera",
    },
]


class Command(BaseCommand):
    help = "Mengisi database dengan data Experience, Project, dan grup Editor contoh."

    def handle(self, *args, **options):
        for data in EXPERIENCES:
            title = data.pop("title")
            _, created = Experience.objects.get_or_create(title=title, defaults=data)
            self.stdout.write(
                f"Experience '{title}' {'created!' if created else 'already exists.'}"
            )

        for data in PROJECTS:
            name = data.pop("name")
            _, created = Project.objects.get_or_create(name=name, defaults=data)
            self.stdout.write(
                f"Project '{name}' {'created!' if created else 'already exists.'}"
            )

        self.seed_editor_group()

        self.stdout.write(self.style.SUCCESS("Seeding complete."))

    def seed_editor_group(self):
        group, created = Group.objects.get_or_create(name=EDITOR_GROUP_NAME)

        permissions = Permission.objects.filter(
            content_type__app_label="main",
            codename__in=EDITOR_PERMISSION_CODENAMES,
        )
        group.permissions.set(permissions)

        codenames = ", ".join(sorted(p.codename for p in permissions))
        self.stdout.write(
            f"Group '{EDITOR_GROUP_NAME}' {'created!' if created else 'already exists.'} "
            f"(permissions: {codenames})"
        )
