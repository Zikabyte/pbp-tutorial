from django.urls import path

from main.views import (
    create_experience,
    create_project,
    delete_experience,
    delete_project,
    get_experience_json,
    get_projects_json,
    show_experience,
    show_main,
    show_projects,
    update_experience,
    update_project,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),

    # ---------------------------------- Project --------------------------------- #
    path("project/", show_projects, name="show_projects"),
    path("project/add/", create_project, name="create_project"),
    path("project/<uuid:project_id>/edit/", update_project, name="update_project"),
    path("projects/<uuid:project_id>/delete/", delete_project, name="delete_project"),
    path("api/projects/", get_projects_json, name="get_projects_json"),

    # -------------------------------- Experience -------------------------------- #
    path("experience/", show_experience, name="show_experience"),
    path("experience/add/", create_experience, name="create_experience"),
    path("experience/<uuid:experience_id>/edit/", update_experience, name="update_experience"),
    path("experience/<uuid:experience_id>/delete/", delete_experience, name="delete_experience"),
    path("api/experiences/", get_experience_json, name="get_experience_json"),
]
