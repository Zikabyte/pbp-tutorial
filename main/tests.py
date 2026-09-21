import json

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from main.models import Experience, Project


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )
        self.project = Project.objects.create(
            name="Zikapedia",
            description="Portfolio berbasis React oleh Zika.",
            category="web-development",
            project_url="https://pbp.cs.ui.ac.id"
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')
        self.assertContains(response, f'href="{reverse("main:show_projects")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")

    # --------------------------- Experience CRUD Testing -------------------------- #
    def test_create_experience_view_get(self):
        response = self.client.get(reverse("main:create_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience_form.html")

    def test_create_experience_valid_post(self):
        response = self.client.post(reverse("main:create_experience"), data={
            "title": "Mobile Apps Developer Intern at McDonalds",
            "description": "Mengembangkan mobile app.",
            "category": "internship",
        })

        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertTrue(Experience.objects.filter(title="Mobile Apps Developer Intern at McDonalds").exists())

    def test_create_experience_invalid_post_does_not_create(self):
        initial_count = Experience.objects.count()
        response = self.client.post(reverse("main:create_experience"), data={
            "title": "",
            "description": "",
            "category": "internship",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Experience.objects.count(), initial_count)

    def test_update_experience_view_get_prefills_form(self):
        response = self.client.get(reverse("main:update_experience", args=[self.experience.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience_form.html")
        self.assertContains(response, self.experience.title)

    def test_update_experience_valid_post(self):
        response = self.client.post(
            reverse("main:update_experience", args=[self.experience.id]),
            data={
                "title": "Asisten Dosen DDP-1",
                "description": self.experience.description,
                "category": self.experience.category,
            },
        )

        self.assertRedirects(response, reverse("main:show_experience"))
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Asisten Dosen DDP-1")

    def test_update_nonexistent_experience_returns_404(self):
        response = self.client.get(
            reverse("main:update_experience", args=["00000000-0000-0000-0000-000000000000"])
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_experience_post_removes_it(self):
        response = self.client.post(reverse("main:delete_experience", args=[self.experience.id]))

        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertFalse(Experience.objects.filter(id=self.experience.id).exists())

    def test_delete_experience_get_does_not_remove_it(self):
        response = self.client.get(reverse("main:delete_experience", args=[self.experience.id]))

        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertTrue(Experience.objects.filter(id=self.experience.id).exists())

    def test_get_experience_json(self):
        response = self.client.get(reverse("main:get_experience_json"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response["Content-Type"])
        data = json.loads(response.content)
        titles = [entry["fields"]["title"] for entry in data]
        self.assertIn(self.experience.title, titles)

    def test_get_experience_json_filters_by_title(self):
        Experience.objects.create(
            title="Volunteer Mengajar",
            description="Mengajar coding untuk anak-anak.",
            category="volunteer",
        )

        response = self.client.get(reverse("main:get_experience_json"), {"title": "Asisten"})
        data = json.loads(response.content)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["fields"]["title"], self.experience.title)

    # ------------------------------ Project Testing ----------------------------- #
    def test_project_page(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project.html")
        self.assertContains(response, self.project.name)
        self.assertContains(response, self.project.description)
        self.assertContains(response, "href=\"https://pbp.cs.ui.ac.id\"")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_project_page(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_projects"))

        self.assertContains(response, "Belum ada proyek yang ditambahkan.")

    def test_project_model(self):
            self.assertEqual(str(self.project), "Zikapedia")

    # ---------------------------- Project CRUD Testing ---------------------------- #
    def test_create_project_view_get(self):
        response = self.client.get(reverse("main:create_project"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects_form.html")

    def test_create_project_valid_post(self):
        response = self.client.post(reverse("main:create_project"), data={
            "name": "Samudera",
            "description": "Aplikasi pemantau saham.",
            "image_url": "/static/img/project-samudera.png",
            "category": "mobile-development",
            "project_url": "https://github.com/Zikabyte/samudera",
        })

        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertTrue(Project.objects.filter(name="Samudera").exists())

    def test_create_project_invalid_post_does_not_create(self):
        initial_count = Project.objects.count()
        response = self.client.post(reverse("main:create_project"), data={
            "name": "",
            "description": "",
            "category": "general",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Project.objects.count(), initial_count)

    def test_update_project_view_get_prefills_form(self):
        response = self.client.get(reverse("main:update_project", args=[self.project.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects_form.html")
        self.assertContains(response, self.project.name)

    def test_update_project_valid_post(self):
        response = self.client.post(
            reverse("main:update_project", args=[self.project.id]),
            data={
                "name": "Zikapedia v2",
                "description": self.project.description,
                "image_url": "/static/img/project-zikapedia.png",
                "category": self.project.category,
                "project_url": self.project.project_url,
            },
        )

        self.assertRedirects(response, reverse("main:show_projects"))
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, "Zikapedia v2")

    def test_update_nonexistent_project_returns_404(self):
        response = self.client.get(
            reverse("main:update_project", args=["00000000-0000-0000-0000-000000000000"])
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_project_post_removes_it(self):
        response = self.client.post(reverse("main:delete_project", args=[self.project.id]))

        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_delete_project_get_does_not_remove_it(self):
        response = self.client.get(reverse("main:delete_project", args=[self.project.id]))

        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_get_projects_json(self):
        response = self.client.get(reverse("main:get_projects_json"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response["Content-Type"])
        data = json.loads(response.content)
        names = [entry["fields"]["name"] for entry in data]
        self.assertIn(self.project.name, names)

    def test_get_projects_json_filters_by_title_param(self):
        Project.objects.create(
            name="Samudera",
            description="Aplikasi pemantau saham.",
            category="mobile-development",
            project_url="https://github.com/Zikabyte/samudera",
        )

        response = self.client.get(reverse("main:get_projects_json"), {"title": "Zika"})
        data = json.loads(response.content)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["fields"]["name"], self.project.name)

# ----------------- Bonus: Functional Testing w/ Selenium :) ----------------- #
class NavbarFunctionalTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        cls.selenium = webdriver.Chrome(options=options)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_navbar_links_to_all_pages(self):
        self.selenium.get(self.live_server_url)

        self.selenium.find_element(By.LINK_TEXT, "Experience").click()
        self.assertIn(reverse("main:show_experience"), self.selenium.current_url)

        self.selenium.find_element(By.LINK_TEXT, "Project").click()
        self.assertIn(reverse("main:show_projects"), self.selenium.current_url)

        self.selenium.find_element(By.LINK_TEXT, "Profile").click()
        self.assertIn(reverse("main:show_main"), self.selenium.current_url)

    def test_dark_mode_toggle(self):
        self.selenium.get(self.live_server_url)
        html = self.selenium.find_element(By.TAG_NAME, "html")
        toggle = self.selenium.find_element(By.ID, "theme-toggle")

        initial_theme = html.get_attribute("data-theme")
        toggle.click()
        toggled_theme = html.get_attribute("data-theme")

        self.assertNotEqual(toggled_theme, initial_theme)

        self.selenium.refresh()
        html = self.selenium.find_element(By.TAG_NAME, "html")
        self.assertEqual(html.get_attribute("data-theme"), toggled_theme)
