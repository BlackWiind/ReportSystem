from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from reports.models import Report
from users.models import User


class DocumentDataForActions(APIView):
    """ Сервиснове api, принимает id пользователя и id рапорта, возвращяет данные
        для предаставления прав на редоктирование документа.
    """
    my_tags = ['Service_API', ]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['user_id', 'report_id'],
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'report_id': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ),
    )
    def get(self, request):
        print(request.GET)
        try:
            user_id = request.GET.get('user_id')
            document_id = request.GET.get('report_id')
        except:
            return JsonResponse(data={'message': f'Не предоставленны данные пользователя илт документа.'}, status=400)
        try:
            document = Report.objects.filter(id=document_id)[0]
            user = User.objects.filter(id=user_id)[0]
        except ObjectDoesNotExist:
            return JsonResponse(data={'message': 'Несуществует такого пользователя или документа.'}, status=404)

        data_for_return = {
            "status": document.status.name,
            "department": document.creator.department.id,
            "is_closed": document.closed,
            "curator": True if document.curators_group == user.curators_group else False,
            "responsible_user": document.responsible,
            "responsible_economist": document.assigned_economist,
            "responsible_purchasing_specialist": document.assigned_purchasing_specialist,
            "user_group": user.custom_permissions.id,
            "user_department": user.department.id,
        }
        return JsonResponse(data=data_for_return, status=200)
