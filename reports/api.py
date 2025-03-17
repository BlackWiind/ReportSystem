import threading

from click import Parameter
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from reports.filters import ReportFilter
from reports.mail import send_email
from reports.models import Report, Tag, History, WaitingStatusForUser
from reports.permissions import IsSuperuserOrReadOnly
from reports.serializers import ReportRetrieveUpdateSerializer, DraftSerializer, \
    ReportCreateSerializer, TagsSerializer, ReportListSerializer, HistoryUpdateSerializer, \
    WaitingStatusForUserSerializer
from reports.utils.utils import LargeResultsSetPagination, additional_data
from users.models import Statuses


class TagRUD(generics.RetrieveUpdateDestroyAPIView):
    """ Получение, обновление и удаление тега"""
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = [IsSuperuserOrReadOnly]

class TagListAndCreate(generics.ListCreateAPIView):
    """ Получение списка тегов и создание нового тега"""
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [IsSuperuserOrReadOnly]


class DraftListAndCreate(generics.ListCreateAPIView):
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
    serializer_class = ReportCreateSerializer

    def perform_create(self, serializer):
        user = self.request.user
        instance = serializer.save(creator=user, draft=False, curators_group=user.department.curators_group,
                        )
        instance.history.create(user=user,
            text="Рапорт создан.")


class ReportList(generics.ListAPIView):
    """Список рапортов"""
    serializer_class = ReportListSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ReportFilter

    def get_queryset(self):
        return Report.custom_query.not_closed_reports(user=self.request.user)

class ReportRetrieveUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = ReportRetrieveUpdateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'get',]

    def get_queryset(self):
        return Report.objects.all()

    def perform_update(self, serializer):
        instance = serializer.save()
        additional_data(instance, self.request)

class CanIShutDownWaiting(APIView):
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
    def post(self, request, *args, **kwargs):
        try:
            thread = threading.Thread(target=send_email, args=(request.POST['message'], request.POST['user']))
            thread.start()
            return JsonResponse(data={'message': f'Сообщение отправлено'}, status=200)
        except Exception as e:
            return JsonResponse(data={'message': f'Произошла ошибка: {type(e).__name__}, {e}'}, status=400)

class ReportApproveClose(viewsets.ViewSet):
    queryset = Report.objects.all()
    serializer_class = HistoryUpdateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', ]

    def new_history(self, text):
        return History.objects.create(user=self.request.user,text=text)


    @action(detail=True)
    @swagger_auto_schema(request_body=HistoryUpdateSerializer)
    def report_approve(self, request, pk=None):
        instance = get_object_or_404(self.queryset,pk=pk)
        if instance.status.id < 9:
            instance.status = Statuses.objects.get(id=instance.status.id+1)
            instance.history.add(self.new_history("Рапорт одобрен."))
        else:
            instance.closed = True
            instance.history.add(self.new_history("Закупка состоялась."))
        instance.save()
        return Response(status=status.HTTP_200_OK)


    @action(detail=True)
    @swagger_auto_schema(request_body=HistoryUpdateSerializer)
    def report_close(self, request, pk=None):
        instance = get_object_or_404(self.queryset,pk=pk)
        instance.closed = True
        instance.history.add(self.new_history(request.data['text']))
        instance.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True)
    @swagger_auto_schema(request_body=HistoryUpdateSerializer)
    def report_freeze(self, request, pk=None):
        instance = get_object_or_404(self.queryset, pk=pk)
        additional_data(instance, self.request)
        instance.save()
        return Response(status=status.HTTP_200_OK)

