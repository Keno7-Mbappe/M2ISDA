from django.http import HttpResponsePermanentRedirect

CANONICAL_ORIGIN = "https://m2isda.com"
LEGACY_SUFFIX = ".onrender.com"
EXEMPT_PATHS = {"/healthz"}


class CanonicalHostMiddleware:
    """Redirige (301) l'ancienne adresse *.onrender.com vers le domaine officiel.

    /healthz reste accessible : il sert aux contrôles de santé et au réveil automatique.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":")[0].lower()
        if host.endswith(LEGACY_SUFFIX) and request.path not in EXEMPT_PATHS:
            return HttpResponsePermanentRedirect(CANONICAL_ORIGIN + request.get_full_path())
        return self.get_response(request)
