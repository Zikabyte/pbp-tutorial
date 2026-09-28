import json

from django.contrib.auth.models import Group, Permission, User
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
        # Sebagian besar test di kelas ini menganggap kita adalah pemilik
        # portofolio (superuser), karena view create/update/delete sekarang
        # butuh login + permission.
        self.owner = User.objects.create_superuser(
            username="portfolio_owner", password="ownerpass123", email="owner@example.com"
        )
        self.client.login(username="portfolio_owner", password="ownerpass123")

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

    def test_get_experience_json_filters_by_category(self):
        Experience.objects.create(
            title="Volunteer Mengajar",
            description="Mengajar coding untuk anak-anak.",
            category="volunteer",
        )

        response = self.client.get(reverse("main:get_experience_json"), {"category": "volunteer"})
        data = json.loads(response.content)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["fields"]["category"], "volunteer")

    def test_get_experience_json_sorted_by_title_desc(self):
        Experience.objects.create(
            title="Zebra Project",
            description="Contoh pengalaman lain.",
            category="freelance",
        )

        response = self.client.get(reverse("main:get_experience_json"), {"sort": "-title"})
        data = json.loads(response.content)
        titles = [entry["fields"]["title"] for entry in data]

        self.assertEqual(titles, sorted(titles, reverse=True))

    def test_show_experience_defaults_to_sort_by_title(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.context["sort_query"], "title")
        self.assertEqual(response.context["category_query"], "")

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

    def test_get_projects_json_filters_by_category(self):
        Project.objects.create(
            name="Samudera",
            description="Aplikasi pemantau saham.",
            category="mobile-development",
            project_url="https://github.com/Zikabyte/samudera",
        )

        response = self.client.get(reverse("main:get_projects_json"), {"category": "mobile-development"})
        data = json.loads(response.content)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["fields"]["category"], "mobile-development")

    def test_get_projects_json_sorted_by_name_desc(self):
        Project.objects.create(
            name="Alpha Tool",
            description="Contoh proyek lain.",
            category="general",
        )

        response = self.client.get(reverse("main:get_projects_json"), {"sort": "-name"})
        data = json.loads(response.content)
        names = [entry["fields"]["name"] for entry in data]

        self.assertEqual(names, sorted(names, reverse=True))

    def test_get_projects_json_ignores_invalid_sort_value(self):
        response = self.client.get(reverse("main:get_projects_json"), {"sort": "'; DROP TABLE"})

        self.assertEqual(response.status_code, 200)

    def test_show_projects_defaults_to_sort_by_name(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertEqual(response.context["sort_query"], "name")
        self.assertEqual(response.context["category_query"], "")


# ----------------------------------- Auth ----------------------------------- #
class AuthTest(TestCase):
    def test_register_view_get(self):
        response = self.client.get(reverse("main:register"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")

    def test_register_valid_post_creates_user(self):
        response = self.client.post(reverse("main:register"), data={
            "username": "newbie",
            "password1": "SangatAman123!",
            "password2": "SangatAman123!",
        })

        self.assertRedirects(response, reverse("main:login"))
        self.assertTrue(User.objects.filter(username="newbie").exists())

    def test_register_password_mismatch_does_not_create_user(self):
        response = self.client.post(reverse("main:register"), data={
            "username": "newbie2",
            "password1": "SangatAman123!",
            "password2": "TidakSama456!",
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newbie2").exists())

    def test_login_valid_credentials_logs_in_and_sets_cookie(self):
        User.objects.create_user(username="logintest", password="pass12345")

        response = self.client.post(
            reverse("main:login"),
            data={"username": "logintest", "password": "pass12345"},
        )

        self.assertRedirects(response, reverse("main:show_main"))
        self.assertEqual(self.client.session["_auth_user_id"], str(User.objects.get(username="logintest").pk))
        self.assertIn("last_login", response.cookies)

    def test_login_invalid_credentials_does_not_log_in(self):
        response = self.client.post(reverse("main:login"), data={
            "username": "doesnotexist",
            "password": "wrongpass",
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_clears_session_and_cookie(self):
        User.objects.create_user(username="logouttest", password="pass12345")
        self.client.login(username="logouttest", password="pass12345")

        response = self.client.get(reverse("main:logout"))

        self.assertRedirects(response, reverse("main:show_main"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertEqual(response.cookies["last_login"].value, "")


# ------------------------- Permission Management ------------------------ #
class PermissionTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            name="Contoh Proyek",
            description="Deskripsi contoh proyek.",
            category="general",
            image_url="https://example.com/image.png",
            project_url="https://example.com/project",
        )
        self.experience = Experience.objects.create(
            title="Contoh Pengalaman",
            description="Deskripsi contoh pengalaman.",
            category="internship",
        )

        self.owner = User.objects.create_superuser(
            username="owner", password="pass12345", email="owner@example.com"
        )
        self.regular = User.objects.create_user(username="regular", password="pass12345")
        self.editor = User.objects.create_user(username="editor", password="pass12345")

        editor_group, _ = Group.objects.get_or_create(name="Editor")
        editor_group.permissions.set(Permission.objects.filter(
            content_type__app_label="main",
            codename__in=["change_project", "change_experience"],
        ))
        self.editor.groups.add(editor_group)

    # --------------------------------- Visitor -------------------------------- #
    def test_anonymous_visiting_create_project_redirects_to_login(self):
        response = self.client.get(reverse("main:create_project"))

        self.assertRedirects(
            response,
            f"{reverse('main:login')}?next={reverse('main:create_project')}",
        )

    def test_anonymous_visiting_update_experience_redirects_to_login(self):
        response = self.client.get(reverse("main:update_experience", args=[self.experience.id]))

        self.assertRedirects(
            response,
            f"{reverse('main:login')}?next={reverse('main:update_experience', args=[self.experience.id])}",
        )

    # ------------------------------- User ------------------------------ #
    def test_regular_user_cannot_create_project(self):
        self.client.login(username="regular", password="pass12345")

        response = self.client.get(reverse("main:create_project"))

        self.assertEqual(response.status_code, 403)

    def test_regular_user_cannot_update_project(self):
        self.client.login(username="regular", password="pass12345")

        response = self.client.get(reverse("main:update_project", args=[self.project.id]))

        self.assertEqual(response.status_code, 403)

    def test_regular_user_cannot_create_experience(self):
        self.client.login(username="regular", password="pass12345")

        response = self.client.get(reverse("main:create_experience"))

        self.assertEqual(response.status_code, 403)

    # ---------------------------------- Editor ----------------------------------- #
    def test_editor_cannot_create_project(self):
        self.client.login(username="editor", password="pass12345")

        response = self.client.get(reverse("main:create_project"))

        self.assertEqual(response.status_code, 403)

    def test_editor_can_update_project(self):
        self.client.login(username="editor", password="pass12345")

        response = self.client.post(
            reverse("main:update_project", args=[self.project.id]),
            data={
                "name": "Diedit Editor",
                "description": self.project.description,
                "image_url": self.project.image_url,
                "category": self.project.category,
                "project_url": self.project.project_url,
            },
        )

        self.assertRedirects(response, reverse("main:show_projects"))
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, "Diedit Editor")

    def test_editor_cannot_delete_project(self):
        self.client.login(username="editor", password="pass12345")

        response = self.client.post(reverse("main:delete_project", args=[self.project.id]))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_editor_can_update_experience(self):
        self.client.login(username="editor", password="pass12345")

        response = self.client.post(
            reverse("main:update_experience", args=[self.experience.id]),
            data={
                "title": "Diedit Editor",
                "description": self.experience.description,
                "category": self.experience.category,
            },
        )

        self.assertRedirects(response, reverse("main:show_experience"))
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Diedit Editor")

    def test_editor_cannot_delete_experience(self):
        self.client.login(username="editor", password="pass12345")

        response = self.client.post(reverse("main:delete_experience", args=[self.experience.id]))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Experience.objects.filter(id=self.experience.id).exists())

    # ----------------------------- Owner ----------------------------- #
    def test_owner_can_create_and_delete_project(self):
        self.client.login(username="owner", password="pass12345")

        response_create = self.client.post(reverse("main:create_project"), data={
            "name": "Punya Owner",
            "description": "Deskripsi.",
            "image_url": "https://example.com/image.png",
            "category": "general",
            "project_url": "https://example.com/project",
        })
        self.assertRedirects(response_create, reverse("main:show_projects"))

        response_delete = self.client.post(reverse("main:delete_project", args=[self.project.id]))
        self.assertRedirects(response_delete, reverse("main:show_projects"))
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())


# ------------------------------- Star ------------------------------- #
class StarTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            name="Contoh Proyek",
            description="Deskripsi contoh proyek.",
            category="general",
        )
        self.experience = Experience.objects.create(
            title="Contoh Pengalaman",
            description="Deskripsi contoh pengalaman.",
            category="internship",
        )
        self.user = User.objects.create_user(username="starrer", password="pass12345")

    def test_anonymous_cannot_toggle_project_star(self):
        star_url = reverse("main:toggle_project_star", args=[self.project.id])

        response = self.client.post(star_url)

        self.assertRedirects(response, f"{reverse('main:login')}?next={star_url}")
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_logged_in_user_can_star_and_unstar_project(self):
        self.client.login(username="starrer", password="pass12345")
        star_url = reverse("main:toggle_project_star", args=[self.project.id])

        self.client.post(star_url)
        self.assertTrue(self.project.starred_by.filter(pk=self.user.pk).exists())

        self.client.post(star_url)
        self.assertFalse(self.project.starred_by.filter(pk=self.user.pk).exists())

    def test_starring_project_twice_does_not_duplicate(self):
        self.project.starred_by.add(self.user)
        self.project.starred_by.add(self.user)

        self.assertEqual(self.project.starred_by.count(), 1)

    def test_logged_in_user_can_star_and_unstar_experience(self):
        self.client.login(username="starrer", password="pass12345")
        star_url = reverse("main:toggle_experience_star", args=[self.experience.id])

        self.client.post(star_url)
        self.assertTrue(self.experience.starred_by.filter(pk=self.user.pk).exists())

        self.client.post(star_url)
        self.assertFalse(self.experience.starred_by.filter(pk=self.user.pk).exists())


# --------------------------- API Data Safety and Integrity -------------------------- #
class ApiSecurityTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            name="Contoh Proyek",
            description="Deskripsi contoh proyek.",
            category="general",
        )
        self.owner = User.objects.create_superuser(
            username="owner2", password="pass12345", email="owner2@example.com"
        )
        self.starrer = User.objects.create_user(username="starrer2", password="pass12345")
        self.project.starred_by.add(self.starrer)

    def test_anonymous_does_not_see_starred_by_in_json(self):
        response = self.client.get(reverse("main:get_projects_json"))
        data = json.loads(response.content)
        match = next(entry for entry in data if entry["pk"] == str(self.project.id))

        self.assertNotIn("starred_by", match["fields"])

    def test_superuser_sees_starred_by_in_json(self):
        self.client.login(username="owner2", password="pass12345")

        response = self.client.get(reverse("main:get_projects_json"))
        data = json.loads(response.content)
        match = next(entry for entry in data if entry["pk"] == str(self.project.id))

        self.assertIn("starred_by", match["fields"])
        self.assertEqual(match["fields"]["starred_by"], [["starrer2"]])


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

        self.selenium.find_element(By.LINK_TEXT, "Projects").click()
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
