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
        self.assertContains(response, f'href="{reverse("main:show_project")}"')

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

    # ------------------------------ Project Testing ----------------------------- #
    def test_project_page(self):
        response = self.client.get(reverse("main:show_project"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project.html")
        self.assertContains(response, self.project.name)
        self.assertContains(response, self.project.description)
        self.assertContains(response, "href=\"https://pbp.cs.ui.ac.id\"")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_project_page(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_project"))

        self.assertContains(response, "Belum ada project yang ditambahkan.")

    def test_project_model(self):
            self.assertEqual(str(self.project), "Zikapedia")

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
        self.assertIn(reverse("main:show_project"), self.selenium.current_url)

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
