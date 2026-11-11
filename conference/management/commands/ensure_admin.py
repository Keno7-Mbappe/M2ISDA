"""Crée ou met à jour le compte administrateur à partir des variables d'environnement ADMIN_USERNAME et ADMIN_PASSWORD.

Utilisé au déploiement : le mot de passe n'est jamais écrit dans le code ni dans le dépôt.
Sans ces variables, la commande ne fait rien.
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crée/met à jour l'administrateur depuis ADMIN_USERNAME / ADMIN_PASSWORD (variables d'environnement)."

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME", "").strip()
        password = os.environ.get("ADMIN_PASSWORD", "")
        if not username or not password:
            self.stdout.write("ensure_admin : ADMIN_USERNAME / ADMIN_PASSWORD absents, rien à faire.")
            return
        User = get_user_model()
        user, created = User.objects.get_or_create(username=username)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()
        self.stdout.write(f"ensure_admin : compte « {username} » {'créé' if created else 'mis à jour'}.")
