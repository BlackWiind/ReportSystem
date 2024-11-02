from django import template

register = template.Library()

ADMIN_PAGE = {'Админка': 'admin:index'}
NEW_USER = {'Новый пользователь': 'users:register'}


@register.simple_tag()
def get_links(user):
    groups = user.groups.all()
    available_statuses = {}
    for group in groups:
        available_statuses = {link.name: link.link for link in group.customgroups.links.all()}
    if user.is_superuser:
        available_statuses |= NEW_USER | ADMIN_PAGE
    return available_statuses
