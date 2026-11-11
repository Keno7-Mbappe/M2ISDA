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

## Liste des participants et tableau de bord
La rubrique « Participants » (liste alphabétique avec recherche, carte du monde) lit la table `Participant` de la base de données.
La liste initiale est insérée par la migration `0002_participants_initiaux`.

Le tableau de bord se trouve à l’adresse `/admin/` : ajout, modification, suppression, ajout d’une liste collée depuis Excel,
export CSV. Il faut un compte : `python manage.py ensure_admin` le crée ou met à jour à partir des variables d’environnement
`ADMIN_USERNAME` et `ADMIN_PASSWORD` (jamais dans le dépôt). `build.sh` l’exécute à chaque déploiement.

### Base de données en production
Sur Render (offre gratuite), le disque est effacé à chaque redémarrage : avec SQLite, les participants ajoutés dans le tableau de bord
seraient perdus. Il faut donc une base externe et la variable d’environnement `DATABASE_URL`
(par exemple une base PostgreSQL gratuite chez Neon ou Supabase). `dj-database-url` et `psycopg` sont déjà configurés.
Variables à définir sur Render : `DATABASE_URL`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`.
