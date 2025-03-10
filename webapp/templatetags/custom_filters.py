from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    """Filtro para acceder a valores dentro de un diccionario en las plantillas de Django."""
    return dictionary.get(key, 0)  # Devuelve 0 si la clave no existe

@register.filter
def getattr(obj, attr_name):
    """Filtro para obtener atributos dinámicamente en Django templates."""
    if hasattr(obj, attr_name):
        return getattr(obj, attr_name)
    return None  # Devuelve None si el atributo no existe

@register.filter
def calculate_total(row, capmo_labels):
    """
    Calcula la suma total de todas las columnas (meses) de una fila.
    row: Es el diccionario de la fila actual.
    capmo_labels: Son los meses disponibles en la tabla.
    """
    return sum(row.get(capmo, 0) for capmo in capmo_labels)

@register.filter
def get_value(dictionary, key):
    """ Devuelve el valor de un diccionario dado un key o 0 si no existe. """
    return dictionary.get(key, 0)

@register.filter
def title_case(value):
    """Convierte cada palabra en mayúscula inicial (Title Case)"""
    if not isinstance(value, str):
        return value
    return ' '.join(word.capitalize() for word in value.split())
