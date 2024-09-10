from django import template

register = template.Library()

CREATE = {'Создать': 'create-ticket'}
QUEUE = {'Консультации': 'ticket-queue'}
OI_DASHBOARD = {'Рабочий стол': 'dashboard'}
CHANGE = {'Статус': 'change_status'}
PROFILES = {'Профили пользователей': 'users:profiles'}
ADMIN_PAGE = {'Админка': 'admin-page'}
MED_ORGS = {'Список МО': 'users:medical-organizations'}


@register.simple_tag()
def get_links(user):
    groups = user.groups.all()
    links_list = {}
    for group in groups:
        if group.name == 'operator':
            links_list = links_list | CREATE | QUEUE | PROFILES
        if group.name == 'user-md':
            links_list |= QUEUE
        if group.name == 'oi-staff':
            links_list |= OI_DASHBOARD | CHANGE | MED_ORGS
        if user.is_superuser:
            links_list |= ADMIN_PAGE
    return links_list