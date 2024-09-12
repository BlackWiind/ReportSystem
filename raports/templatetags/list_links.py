from django import template

register = template.Library()

CREATE = {'Создать': '#'}
QUEUE = {'Консультации': '#'}
OI_DASHBOARD = {'Рабочий стол': '#'}
CHANGE = {'Статус': '#'}
PROFILES = {'Профили пользователей': '#'}
ADMIN_PAGE = {'Админка': '#'}
MED_ORGS = {'Список МО': '#'}


@register.simple_tag()
def get_links(user):
    groups = user.groups.all()
    links_list = {}
    for group in groups:
        if group.name == 'user':
            links_list = links_list | CREATE | QUEUE | PROFILES
        if user.is_superuser:
            links_list |= ADMIN_PAGE
    return links_list
