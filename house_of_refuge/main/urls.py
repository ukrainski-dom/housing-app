from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import TemplateView, RedirectView

import house_of_refuge.main.views as views

app_name = "main"
urlpatterns = [
    path("", views.home, name="home"),
    path("page/<str:page_name>", views.home, name="home"),
    path("map/", views.home, name="home"),
    path("drogowskaz/", login_required(TemplateView.as_view(template_name="main/guidepost.html")), name="guidepost"),
    path("healthz/", views.healthcheck, name="health"),
    path("statsy/", views.activity_stats_view, name="health"),
    path("share", views.home, name="home-share"),
    path("find", views.home, name="home-find"),
    path("privacy/", views.home, name="home-priv"),

    path("shelter/", RedirectView.as_view(url=settings.SHELTER_FORM_URL, permanent=True)),

    path("edit/", views.edit, name="host-edit"),
    path("jazda/", views.housing_list, name="jazda"),
    path("jazda/stolik/", login_required(views.home), name="home-stolik"),

    # API
    path("api/edit", views.get_form_data, name="form_data"),
    path("api/zasoby", views.get_resources, name="zasoby_get"),
    path("api/zgloszenia", views.get_submissions, name="zgloszenia_get"),

    path("api/latest/subs/", views.latest_submission, name="latest_subs"),
    path("api/latest/resources/", views.latest_resource, name="latest_resources"),

    path("api/helped/", views.get_helped_count, name="helped-count"),
    path("api/update_note/<int:resource_id>", views.update_resource_note, name="note_update"),
    path("api/zglos", views.create_submission, name="zgloszenie_create"),
    path("api/stworz_zasob", views.create_resource, name="zasob_create"),

    path("api/stworz_zasob_integration/<str:uuid>", views.create_resource_integration, name="zasob_create_integration"),
    path("api/zglos_integration/<str:uuid>", views.create_submission_integration, name="zgloszenie_create_integration"),

    path("api/housing_resource", views.create_resource_integration_v2, name="zasob_create_integration_v2"),
    path("api/submission", views.create_submission_integration_v2, name="zgloszenie_create_integration_v2"),

    path("api/match_found", views.resource_match_found, name="match_found"),
    path("api/sub/update/<int:sub_id>", views.update_sub, name="sub_update"),
    path("api/check_limit", views.check_submission_limit, name="check_limit"),

    path("api/resource/update/<int:resource_id>", views.update_resource, name="resource_update"),

    path("api/send_email_token", views.send_email_with_edit_token, name="send_email_token"),
    path("api/menu_pages", views.get_menu_pages, name="get_menu_pages"),

    path("api/stats/", views.get_stats_data, name="get_stats_data"),
]
