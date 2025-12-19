import threading

from django_filters import rest_framework as filters
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from reports.filters import ReportFilter
from reports.mail import send_email
from reports.models import Report, Tag, History, WaitingStatusForUser, SourcesOfFunding
from reports.permissions import IsSuperuserOrReadOnly
from reports.serializers import ReportRetrieveUpdateSerializer, DraftSerializer, \
    ReportCreateSerializer, TagsSerializer, ReportListSerializer, HistoryUpdateSerializer, \
    WaitingStatusForUserSerializer, ReportPatchSerializer, SourcesOfFundingSerializer, ReportEditableSerializer
from reports.tasks import async_create_new_notification
from reports.utils.signals import tracked_changes
from reports.utils.unloads import PdfReports
from reports.utils.utils import LargeResultsSetPagination
from users.models import Statuses


class TagRUD(generics.RetrieveUpdateDestroyAPIView):
    """ Получение, обновление и удаление тега"""
    my_tags = ['Tags',]

    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = [IsSuperuserOrReadOnly]

class TagListAndCreate(generics.ListCreateAPIView):
    """ Получение списка тегов и создание нового тега"""
    my_tags = ['Tags', ]

    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [IsSuperuserOrReadOnly]

class DraftListAndCreate(generics.ListCreateAPIView):
    """ Получение списка черновиков и создание нового черновика"""
    my_tags = ['Drafts',]

    serializer_class = DraftSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Report.custom_query.not_closed_draft(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        instance = serializer.save(creator=user, draft=True, curators_group=user.department.curators_group,
                                   )
        instance.history.create(user=user,
                                text="Рапорт создан.")

class ReportCreate(generics.CreateAPIView):
    """ Создание нового рапорта"""
    my_tags = ['Reports', ]

    serializer_class = ReportCreateSerializer

    def perform_create(self, serializer):
        user = self.request.user
        instance = serializer.save(creator=user, draft=False,
                                   curators_group=user.department.curators_group)
        instance.parents.all().update(closed=True)
        instance.history.create(user=user,
            text="Рапорт создан.")
        async_create_new_notification.delay(instance.pk)

class ReportList(generics.ListAPIView):
    """Список рапортов"""
    serializer_class = ReportListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ReportFilter
    my_tags = ['Reports', ]

    def get_queryset(self):
        return Report.custom_query.not_closed_reports(user=self.request.user)

class ReportRetrieveUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = ReportRetrieveUpdateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'get',]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    my_tags = ['Reports', ]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return ReportPatchSerializer
        return super(ReportRetrieveUpdate, self).get_serializer_class()

    def get_queryset(self):
        return Report.objects.all()

    def perform_update(self, serializer):
        instance = serializer.save()
        changes = tracked_changes.changes.pop(instance.pk, {})
        m2m_changes = tracked_changes.m2m_changes.pop(instance.pk, {})
        all_changes = {**changes, **m2m_changes}
        if all_changes:
            changes_list = [f"{key}: {value}" for key, value in all_changes.items()]
            changes_text =  "Изменения в следующих полях: " + "; ".join(changes_list)
            instance._add_history_entry(self.request.user,changes_text)
        async_create_new_notification.delay(instance.pk)

class CanIShutDownWaiting(APIView):
    my_tags = ['Other', ]
    @swagger_auto_schema(
        query_serializer=WaitingStatusForUserSerializer,
        operation_description="Create a post object"
    )
    def get(self, request):
        try:
            _ = WaitingStatusForUser.objects.get(sender=request.user, report=request.GET.get('report'))
            return JsonResponse(data={'message': True}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse(data={'message': False}, status=200)
        except Exception as e:
            return JsonResponse(data={'message': f'Произошла ошибка: {type(e).__name__}, {e}'}, status=400)

class Feedback(APIView):
    permission_classes = [IsAuthenticated]
    my_tags = ['Other', ]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['message'],
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING,
                                        max_length=255)
                }
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING,
                                              max_length=255)
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            thread = threading.Thread(target=send_email, args=(self.request.data['message'], request.user))
            thread.start()
            return JsonResponse(data={'message': f'Сообщение отправлено'}, status=200)
        except Exception as e:
            return JsonResponse(data={'message': f'Произошла ошибка: {type(e).__name__}, {e}'}, status=400)

class ReportApproveClose(viewsets.ViewSet):
    queryset = Report.objects.all()
    serializer_class = HistoryUpdateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', ]
    my_tags = ['Reports', ]

    def new_history(self, text):
        return History.objects.create(user=self.request.user,text=text)


    @action(detail=True)
    @swagger_auto_schema(request_body=HistoryUpdateSerializer)
    def report_approve(self, request, pk=None):
        instance = get_object_or_404(self.queryset,pk=pk)
        if instance.status.is_final:
            instance.close_report(self.request.user, "Закупка состоялась.")
        else:
            if request.user.custom_permissions.name == 'curator':
                instance.print_form.save(*PdfReports(instance.pk).create_new_file())
            text = request.data.get('text', "Рапорт одобрен.")
            instance.next_status(self.request.user, text)
        instance.save()
        async_create_new_notification.delay(instance.pk)
        return Response(status=status.HTTP_200_OK)


    @action(detail=True)
    @swagger_auto_schema(request_body=HistoryUpdateSerializer)
    def report_close(self, request, pk=None):
        instance = get_object_or_404(self.queryset,pk=pk)
        instance.close_report(self.request.user, request.data['text'])
        async_create_new_notification.delay(instance.pk)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True)
    @swagger_auto_schema(request_body=HistoryUpdateSerializer)
    def report_freeze(self, request, pk=None):
        # Требуется переименовать после проверки работоспособности
        instance = get_object_or_404(self.queryset, pk=pk)
        instance.prev_status(self.request.user, request.data['text'])
        async_create_new_notification.delay(instance.pk)
        return Response(status=status.HTTP_200_OK)

class Archive(generics.ListAPIView):
    """Архив"""
    serializer_class = ReportListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ReportFilter
    my_tags = ['Archive', ]

    def get_queryset(self):
        return Report.objects.filter(closed=True)

class SourcesOfFundingListView(generics.ListAPIView):
    my_tags = ['Other', ]
    serializer_class = SourcesOfFundingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LargeResultsSetPagination
    queryset = SourcesOfFunding.objects.all()

class ReportListAll(generics.ListAPIView):
    """Список всех рапортов, независящий от роли юзера"""
    serializer_class = ReportListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ReportFilter
    my_tags = ['Reports', ]

    def get_queryset(self):
        return Report.objects.filter(draft=False, closed=False)

class ReportEditableRetrieveUpdateApiView(generics.RetrieveUpdateAPIView):
    "Api получение и изменение метки редактирования для рапорта."
    serializer_class = ReportEditableSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'get', ]
    my_tags = ['Reports', ]

class ReportStatusCrutchApiView(APIView):
    """ Костыль. Меняет статус между Регер и Пестряковой"""
    def post(self, request, pk):
        try:
            report = Report.objects.get(pk=pk)
        except Report.DoesNotExist:
            return Response({"detail": "Report not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            if report.status.name == "reger":
                report.set_status_manually(self.request.user, Statuses.objects.get(name='pestryakova'))
            elif report.status.name == "pestryakova":
                report.set_status_manually(self.request.user, Statuses.objects.get(name='reger'))
            return Response({"detail": "Статус обновлён"})
        except Exception as e:
            return Response({"detail": f"Статус не изменён. Причина: {e}", "current_status": report.status.name})

