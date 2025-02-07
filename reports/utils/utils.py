from django.db.models import Q
from django.http import JsonResponse

from reports.models import Report
import pymorphy2

from users.models import VocationsSchedule, User, CustomGroups


def get_queryset_dependent_group(user):
    available_statuses = list(user.groups.values_list('customgroups__statuses', flat=True))
    set_for_return = None
    parameters = {'status__in': available_statuses}
    if 'curator' in user.groups.values_list('name', flat=True):
        parameters['curators_group'] = user.curators_group
    if user.is_superuser:
        set_for_return = Report.objects.all()
    else:
        set_for_return = Report.objects.filter(Q(**parameters) | Q(creator=user) | Q(assigned_purchasing_specialist=user))
    return set_for_return.exclude(status__status__in=['rejected', 'done'])


def word_to_genitive(word: str) -> str:
    morph = pymorphy2.MorphAnalyzer()
    parsed_word = morph.parse(word)[0]
    word = parsed_word.inflect({'gent'}).word
    return word.capitalize()


def ajax_decoder(request_data) -> dict:
    data = request_data.POST.dict()
    data.pop('csrfmiddlewaretoken', None)
    data.pop('sources_of_funding', None)
    data.pop('pk', None)
    data.pop('files', None)
    return data


def update_status(pk, request):
    report = Report.objects.filter(pk=pk)
    report.update(**ajax_decoder(request))
    for q in report:
        q.history.create(user=request.user, action=q.status)
    return True

def new_vocation(vocation_user, deputy, vocation_start, vocation_end):
    if vocation_end <= vocation_start:
        return JsonResponse(data={'message': 'Дата окончания отпуска должна быть позже даты начала.'}, status=403)
    deputy = User.objects.get(pk=deputy)
    if vocation_user == deputy:
        return JsonResponse(data={'message': 'Вы не можете замещать самого себя.'}, status=403)
    try:
        group = vocation_user.groups.all()[0].name
        VocationsSchedule.objects.create(vocation_start=vocation_start, vocation_end=vocation_end,
                                        vocation_user=vocation_user, deputy=deputy,
                                        group=CustomGroups.objects.get(name=group))
        return JsonResponse(data={'message': 'Успешно'}, status=200)
    except:
        return JsonResponse(data={'message': 'Не получилось создать запись об отпуске'}, status=403)
