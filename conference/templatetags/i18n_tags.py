from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def t(fr, en=None):
    """Texte bilingue : le français est rendu, l'anglais est échangé côté client."""
    if not en or en == fr:
        return fr
    return format_html('<span data-en="{}">{}</span>', en, fr)
