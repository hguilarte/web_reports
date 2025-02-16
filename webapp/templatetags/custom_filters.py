from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    """Filtro para acceder a valores dentro de un diccionario en las plantillas de Django."""
    return dictionary.get(key, 0)  # Devuelve 0 si la clave no existe
