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
        operation_summary="Данные документа для проверки прав редактирования",
        operation_description="Сервисный GET-запрос. Принимает user_id и report_id в query-параметрах "
                              "и возвращает информацию о статусе документа и правах пользователя.",
        manual_parameters=[
            openapi.Parameter(
                name='user_id',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description='ID пользователя, для которого проверяются права'
            ),
            openapi.Parameter(
                name='report_id',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description='ID рапорта / документа (Report)'
            ),
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, description="Название статуса документа"),
                    "department": openapi.Schema(type=openapi.TYPE_INTEGER,
                                                 description="ID отдела создателя документа"),
                    "is_closed": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Признак закрытия документа"),
                    "curator": openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                              description="Является ли пользователь куратором"),
                    "responsible_user": openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                       description="Является ли пользователь ответственным"),
                    "responsible_economist": openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                            description="Является ли пользователь назначенным экономистом"),
                    "responsible_purchasing_specialist": openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                        description="Является ли пользователь специалистом по закупкам"),
                    "user_group": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID группы прав пользователя"),
                    "user_department": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID отдела пользователя"),
                }
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, max_length=255)
                }
            ),
            404: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, max_length=255)
                }
            ),
        }
    )
    def get(self, request):
        user_id_str = request.GET.get('user_id')
        document_id_str = request.GET.get('report_id')

        if not user_id_str or not document_id_str:
            return JsonResponse(
                data={'message': 'Не предоставлены данные пользователя или документа.'},
                status=400
            )

        try:
            user_id = int(user_id_str)
            document_id = int(document_id_str)
        except (TypeError, ValueError):
            return JsonResponse(
                data={'message': 'Неверный формат ID пользователя или документа.'},
                status=400
            )

        try:
            document = Report.objects.get(id=document_id)
            user = User.objects.get(id=user_id)
        except Report.DoesNotExist:
            return JsonResponse(
                data={'message': 'Несуществует такого документа.'},
                status=404
            )
        except User.DoesNotExist:
            return JsonResponse(
                data={'message': 'Несуществует такого пользователя.'},
                status=404
            )

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
