from django import template

register = template.Library()

AGREEMENT = {'Согласовать': ''}
REJECT = {'Отказ': '/'}
WAITING = {'Ожидание': '/'}
TRANSFER = {'Передача': '/'}
UNIFICATION = {'Объеденение': '#/'}


ADMIN_PAGE = {'Админка': 'raports:admin_page'}
MED_ORGS = {'Список МО': '#'}
NEW_USER = {'Новый пользователь': 'users:register'}


@register.simple_tag()
def get_buttons(user):
    groups = user.groups.all()
    links_list = {}
    for group in groups:
        if group.name == 'user-creator':
            links_list = links_list | REJECT
        elif group.name == 'curator':
            links_list = links_list | AGREEMENT | REJECT | WAITING | TRANSFER | UNIFICATION
    if user.is_superuser:
        links_list |= AGREEMENT | REJECT | WAITING | TRANSFER | UNIFICATION
    return links_list
