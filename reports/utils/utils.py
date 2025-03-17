from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework.pagination import PageNumberPagination

from reports.models import Report, WaitingStatusForUser
import pymorphy2

from users.models import VocationsSchedule, User, CustomPermissions


def get_queryset_dependent_group(user):
    return Report.objects.all()


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
                                        group=CustomPermissions.objects.get(name=group))
        return JsonResponse(data={'message': 'Успешно'}, status=200)
    except:
        return JsonResponse(data={'message': 'Не получилось создать запись об отпуске'}, status=403)

def history_add(instance, request, text=None):
    if text is None:
        my_list = [instance._meta.get_field(x).verbose_name for x in list(request.data.keys())]
        text = f"Изменеия в следующих полях: {' '.join(my_list)}"
    instance.history.create(
        user=request.user,
        text=text
    )

def change_waiting_status(instance, request) -> str:
    receiver = instance.responsible if instance.responsible else instance.creator
    text = None
    if instance.waiting:
        _ = WaitingStatusForUser.objects.create(
            sender=request.user, receiver=receiver, report=instance)
        text = f'Установлен статус "Ожидание": {request.data["text"]}'
    else:
        try:
            _ = WaitingStatusForUser.objects.filter(
                sender=request.user, receiver=receiver, report=instance).delete()
        except ObjectDoesNotExist:
            pass
        text = 'Статус "Ожидание" снят'
    return text

def additional_data(instance, request):
    text = None
    if 'waiting' in request.data:
        text = change_waiting_status(instance, request)
    history_add(instance, request, text)





class LargeResultsSetPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 1000