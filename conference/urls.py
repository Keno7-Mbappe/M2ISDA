from django.urls import path

from . import dashboard, views

urlpatterns = [
    path("", views.index, name="index"),
    path("healthz", views.healthz, name="healthz"),
    path("robots.txt", views.robots_txt, name="robots"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap"),
    path("modele-resume.tex", views.tex_template, name="tex_template"),
    # tableau de bord
    path("admin/", dashboard.home, name="dash_home"),
    path("admin/connexion/", dashboard.login_view, name="dash_login"),
    path("admin/deconnexion/", dashboard.logout_view, name="dash_logout"),
    path("admin/participants/ajouter/", dashboard.add, name="dash_add"),
    path("admin/participants/liste/", dashboard.bulk, name="dash_bulk"),
    path("admin/participants/export.csv", dashboard.export_csv, name="dash_export"),
    path("admin/participants/<int:pk>/", dashboard.edit, name="dash_edit"),
    path("admin/participants/<int:pk>/supprimer/", dashboard.delete, name="dash_delete"),
]
