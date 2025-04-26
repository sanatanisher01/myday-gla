from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """
    Split a string by the given delimiter and return the list.
    Usage: {{ value|split:"/" }}
    """
    return value.split(arg)

@register.filter
def get_item(value, index):
    """
    Get an item from a list by index.
    Usage: {{ value|split:"/"|get_item:"-1" }}
    """
    try:
        index = int(index)
        return value[index]
    except (IndexError, ValueError):
        return ""
