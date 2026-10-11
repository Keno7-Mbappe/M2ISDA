from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("healthz", views.healthz, name="healthz"),
    path("modele-resume.tex", views.tex_template, name="tex_template"),
]
