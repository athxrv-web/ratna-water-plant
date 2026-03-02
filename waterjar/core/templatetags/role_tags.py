from django import template

register = template.Library()


@register.filter
def is_owner(user):
    """Usage in template: {% if user|is_owner %}"""
    return user.is_authenticated and user.role == "owner"


@register.filter
def is_staff_role(user):
    """Usage in template: {% if user|is_staff_role %}"""
    return user.is_authenticated and user.role == "staff"