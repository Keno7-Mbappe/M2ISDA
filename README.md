# M2ISDA 2027 — site Django

## Lancer en local
    pip install -r requirements.txt
    set DEBUG=True        (PowerShell : $env:DEBUG="True")
    python manage.py runserver

## Déployer sur Render
1. Pousser ce dossier sur un dépôt GitHub.
2. Render > New > Blueprint > choisir le dépôt (il lit `render.yaml`).
   Ou "Web Service" manuel : Build `./build.sh`, Start `gunicorn config.wsgi:application`.
3. Variables : `SECRET_KEY` (générée), `DEBUG=False`, `PYTHON_VERSION=3.13.5`.
