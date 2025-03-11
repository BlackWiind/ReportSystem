from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from reports.filters import ReportFilter
from reports.models import Report, Tag, History
from reports.permissions import IsSuperuserOrReadOnly
from reports.serializers import ReportRetrieveUpdateSerializer, DraftSerializer, \
    ReportCreateSerializer, TagsSerializer, ReportListSerializer, HistoryUpdateSerializer
from reports.utils.utils import LargeResultsSetPagination


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
        my_list = [instance._meta.get_field(x).verbose_name for x in list(self.request.data.keys())]
        instance.history.create(
            user=self.request.user,
            text=f"Изменеия в следующих полях: {' '.join(my_list)}"
        )

# class ReportApprove(generics.UpdateAPIView):
#     queryset = Report.objects.all()
#     serializer_class = HistoryUpdateSerializer
#     permission_classes = [IsAuthenticated]
#
#     def perform_update(self, serializer):
#         instance = Report.objects.get(pk=self.kwargs['pk'])
#         if instance.status.id < 9:
#             instance.status.id += 1
#             instance.history.create(user=self.request.user,
#                 text="Рапорт одобрен.")
#         else:
#             instance.closed = True
#             instance.history.create(user=self.request.user,
#                                     text="Закупка состоялась.")
#
# class ReportClose(generics.UpdateAPIView):
#     queryset = Report.objects.all()
#     serializer_class = HistoryUpdateSerializer
#     permission_classes = [IsAuthenticated]
#     http_method_names = ['patch',]
#
#     def perform_update(self, serializer):
#         instance = self.get_object()
#         instance.closed = True
#         instance.history.create(user=self.request.user,
#                                     text=serializer.data['text'])
#         instance.save()

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
            instance.status.id += 1
            instance.history.add(self.new_history("Рапорт одобрен."))
        else:
            instance.closed = True
            instance.history.add(self.new_history("Закупка состоялась."))
        return Response(status=status.HTTP_200_OK)


    @action(detail=True)
    @swagger_auto_schema(request_body=HistoryUpdateSerializer)
    def report_close(self, request, pk=None):
        instance = get_object_or_404(self.queryset,pk=pk)
        instance.closed = True
        instance.history.add(text=request.data['text'])
        instance.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True)
    @swagger_auto_schema(request_body=HistoryUpdateSerializer)
    def report_freeze(self, request, pk=None):
        instance = get_object_or_404(self.queryset, pk=pk)
        if instance.waiting:
            instance.waiting = False
            instance.history.add('Блокировка снята')
        else:
            instance.waiting = True
            instance.history.add(text=request.data['text'])
        instance.save()
        return Response(status=status.HTTP_200_OK)

