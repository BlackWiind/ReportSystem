from django import template

register = template.Library()

CREATE = {'Создать': 'raports:create_raport'}
LIST = {'Список': 'raports:list'}
OI_DASHBOARD = {'Рабочий стол': '#'}
CHANGE = {'Статус': '#'}
PROFILES = {'Профили пользователей': '#'}
ADMIN_PAGE = {'Админка': 'raports:admin_page'}
MED_ORGS = {'Список МО': '#'}
NEW_USER = {'Новый пользователь': 'users:register'}


@register.simple_tag()
def get_links(user):
    groups = user.groups.all()
    links_list = {}
    for group in groups:
        if group.name == 'user':
            links_list = links_list | CREATE | PROFILES
    if user.is_superuser:
        links_list |= CREATE | LIST | NEW_USER | ADMIN_PAGE
    return links_list
