from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Uso: {{ dict|get_item:key }}
    Obtém um item de um dicionário na template
    """
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def add_class(field, css_class):
    """
    Adiciona classe CSS a um campo de formulário
    Uso: {{ form.field|add_class:"class-name" }}
    """
    return field.as_widget(attrs={"class": css_class})

@register.filter
def multiply(value, arg):
    """
    Multiplica um valor
    Uso: {{ value|multiply:2 }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
