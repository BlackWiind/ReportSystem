from django import template
import raports.strings as st

register = template.Library()

AGREEMENT = {'Согласовать': st.APPROVE}
REJECT = {'Отказ': st.REJECT}
WAITING = {'Ожидание': st.WAITING}
TRANSFER = {'Передача': st.TRANSFER}
UNIFICATION = {'Объеденение': st.UNIFICATION}
TRANSFER_TO_PERFORMER = {'Передать исполнителю': st.TRANSFER_TO_PERFORMER}


@register.simple_tag()
def get_buttons(user):
    groups = user.groups.all()
    links_list = {}
    for group in groups:
        if group.name == st.USER_CREATOR:
            links_list |= REJECT
        elif group.name == st.CURATOR:
            links_list |= AGREEMENT | REJECT | WAITING | TRANSFER | UNIFICATION
        elif group.name == st.CHIEF_MEDICAL:
            links_list |= AGREEMENT | REJECT | WAITING
        elif group.name == st.PURCHASING_BOSS:
            links_list |= TRANSFER_TO_PERFORMER
    if user.is_superuser:
        links_list |= AGREEMENT | REJECT | WAITING | TRANSFER | UNIFICATION
    return links_list
