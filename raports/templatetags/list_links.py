from django import template
import raports.strings as st

register = template.Library()

CREATE = {'Создать': 'raports:create_raport'}
LIST = {'Список': 'raports:list'}
ARCHIVE = {'Архив': 'raports:archive'}
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
        if group.name == st.USER_CREATOR:
            links_list |= CREATE
        elif group.name == st.CURATOR:
            links_list |= CREATE
    if user.is_superuser:
        links_list |= CREATE | NEW_USER | ADMIN_PAGE
    links_list |= LIST | ARCHIVE
    return links_list
