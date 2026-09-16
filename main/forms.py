from django.forms import ModelForm, TextInput, Textarea, URLInput, Select

from main.models import Project

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "image_url",
            "category",
            "project_url",
        ]

        labels = {
            "name": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "image_url": "URL Gambar Proyek",
            "category": "Kategori Proyek",
            "project_url": "URL Proyek",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan Proyekmu",
                    "rows": 3,
                }
            ),
            "image_url": URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000",
                }
            ),
            "project_url": URLInput(
                attrs={
                    "placeholder": "https://github.com/FisioMate",
                }
            ),
            "category": Select(
                attrs={
                    "class": "form-select",  # Opsional: tambahkan class CSS jika pakai Tailwind/Bootstrap
                }
            ),
        }