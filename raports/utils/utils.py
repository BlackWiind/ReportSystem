from django.db.models import Q

from raports.models import Raport

import pymorphy2


def get_queryset_dependent_group(user):
    available_statuses = list(user.groups.values_list('customgroups__statuses', flat=True))
    set_for_return = None
    parameters = {'status__in': available_statuses}
    if 'curator' in user.groups.values_list('name', flat=True):
        parameters['curators_group'] = user.curators_group
    if user.is_superuser:
        set_for_return = Raport.objects.all()
    else:
        set_for_return = Raport.objects.filter(Q(**parameters) | Q(creator=user))
    return set_for_return.exclude(status__status__in=['rejected', 'done'])


# def change_raport_status_by_request(user, pk: int, action: str):
#     raport = Raport.objects.get(pk=pk)
#     new_status: str
#     try:
#
#         if action in [st.REJECT, st.WAITING]:
#             new_status = action
#         elif action == st.APPROVE:
#             new_status = new_status_by_approve(user)
#         raport.history.create(user=user, action=st.STATUSES[new_status])
#         raport.status = new_status
#         raport.save()
#
#         return True
#     except:
#         return False


# def new_status_by_approve(user):
#     new_status: str
#     groups = user.groups.all()
#     for group in groups:
#         if group.name == 'curator':
#             new_status = st.APPROVED_BY_CURATOR
#         elif group.name == 'chief_medical':
#             new_status = st.APPROVED_BY_DIRECTOR
#     return new_status


def word_to_genitive(word: str) -> str:
    morph = pymorphy2.MorphAnalyzer()
    parsed_word = morph.parse(word)[0]
    word = parsed_word.inflect({'gent'}).word
    return word.capitalize()


def ajax_decoder(request_data) -> dict:
    data = request_data.POST.dict()
    data.pop('csrfmiddlewaretoken')
    data.pop('pk', None)
    return data
