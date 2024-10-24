from raports.models import Raport
import raports.strings as st

import pymorphy2


def get_queryset_dependent_group(user):
    groups = list(user.groups.values_list('name', flat=True))
    set_for_return = None
    if st.USER_CREATOR in groups:
        set_for_return = Raport.objects.filter(creator=user)
    elif st.CURATOR in groups:
        set_for_return = Raport.objects.filter(curators_group=user.curators_group)
    elif st.CHIEF_MEDICAL in groups:
        set_for_return = Raport.objects.filter(status=st.APPROVED_BY_CURATOR)
    elif st.PURCHASING_BOSS in groups:
        set_for_return = Raport.objects.filter(status=st.APPROVED_BY_DIRECTOR)
    return set_for_return.exclude(status__in=['rejected', 'done'])


def change_raport_status_by_request(user, pk: int, action: str):
    raport = Raport.objects.get(pk=pk)
    new_status: str
    try:

        if action in [st.REJECT, st.WAITING]:
            new_status = action
        elif action == st.APPROVE:
            new_status = new_status_by_approve(user)
        raport.history.create(user=user, action=st.STATUSES[new_status])
        raport.status = new_status
        raport.save()

        return True
    except:
        return False


def new_status_by_approve(user):
    new_status: str
    groups = user.groups.all()
    for group in groups:
        if group.name == 'curator':
            new_status = st.APPROVED_BY_CURATOR
        elif group.name == 'chief_medical':
            new_status = st.APPROVED_BY_DIRECTOR
    return new_status


def word_to_genitive(word: str) -> str:
    morph = pymorphy2.MorphAnalyzer()
    parsed_word = morph.parse(word)[0]
    word = parsed_word.inflect({'gent'}).word
    return word.capitalize()
