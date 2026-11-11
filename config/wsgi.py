"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()


# Au démarrage : applique les migrations (tables et liste initiale des participants) et crée le compte administrateur
# si ADMIN_USERNAME / ADMIN_PASSWORD sont définis. Sans effet sur une base déjà à jour.
if os.environ.get("AUTO_MIGRATE", "1") == "1":
    try:
        from django.core.management import call_command

        call_command("migrate", interactive=False, verbosity=0)
        call_command("ensure_admin", verbosity=0)
    except Exception as exc:  # le site public ne doit pas tomber si la base est momentanément injoignable
        import logging

        logging.getLogger("django").error("Migration au démarrage impossible : %s", exc)
