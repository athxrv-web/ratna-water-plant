from django import template

register = template.Library()

@register.filter
def is_owner(user):
    return user.is_authenticated and user.role == "owner"

@register.filter
def is_staff_role(user):
    return user.is_authenticated and user.role == "staff"
