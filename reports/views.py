import threading

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView
from django_filters.views import FilterView
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, permissions, generics, mixins
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User, CuratorsGroup
from .mail import send_email
from .models import Report, Tag, Files, WaitingStatusForUser, Draft
from reports.utils.form_utils import create_new_report
from .forms import CreateReportForm, AddFilesAndNewPriceForm, AddSourcesOfFundingForm
from .filters import ReportFilter
from reports.utils.utils import get_queryset_dependent_group, update_status
from reports.utils.unloads import create_pdf_unloading
from .permissions import IsOwnerOrReadOnly, IsSuperuserOrReadOnly
from .serializers import DraftCreateSerializer, DraftGetSerializer, DraftListSerializer, TagsListSerializer


class ReportCreateView(CreateView):
    form_class = CreateReportForm
    template_name = 'reports/create_report.html'
    success_url = reverse_lazy('reports:list')

    def form_valid(self, form):
        try:
            create_new_report(self.request, form)
        except Exception as e:
            raise Exception(f"Create new report error: {e.args} {e.__traceback__.tb_lineno}")
        else:
            return HttpResponseRedirect(self.success_url)

    def form_invalid(self, form):
        return super(ReportCreateView, self).form_invalid(form)


class ReportListView(FilterView):
    model = Report
    template_name = 'reports/list.html'
    paginate_by = 5
    filterset_class = ReportFilter

    def get_queryset(self):
        return get_queryset_dependent_group(self.request.user)


class ArchiveListView(FilterView):
    model = Report
    template_name = 'reports/list.html'
    paginate_by = 5
    filterset_class = ReportFilter

    def get_queryset(self):
        return Report.objects.filter(status__status__in=['rejected', 'done'])


class ReportDetailView(DetailView):
    model = Report
    template_name = 'reports/details.html'


def get_curator_groups(request):
    if request.method == 'GET':
        context = {'groups': CuratorsGroup.objects.all()}
        return render(request, 'additional_pages/modal_of_curator_groups.html', context)


def download_pdf_report(request, pk):
    return create_pdf_unloading(pk)


def change_curators_group(request, pk):
    if request.method == 'POST':
        _ = Report.objects.filter(pk=pk).update(curators_group=request.POST['new_group'])
        return JsonResponse(data={'message': 'Рапорт успешно обновлён'})


def get_purchasing_specialist(request):
    if request.method == 'GET':
        context = {'purchasers': User.objects.filter(groups__name='purchasing_specialist')}
        return render(request, 'additional_pages/modal_of_purchasing_specialists.html', context)


class UpdateReportStatusView(UpdateView):
    model = Report
    template_name = 'reports/details.html'
    fields = ['status']

    def post(self, request, *args, **kwargs):
        try:
            update_status(self.get_object().pk, request)
            return JsonResponse(data={'message': 'ok'}, status=200)
        except:
            return JsonResponse(data={'message': 'Произошла ошибка!'}, status=400)


class AddFilesToExistedReport(UpdateView):
    model = Report
    form_class = AddFilesAndNewPriceForm
    template_name = 'additional_pages/add_files_form.html'

    def post(self, request, *args, **kwargs):
        try:
            my_object = self.get_object()
            files = request.FILES.getlist('files')
            update_status(my_object.pk, request)
            if files:
                for file in files:
                    _ = Files.objects.create(file=file)
                    request.FILES['files'] = _
                    my_object.files.add(_)
                my_object.save()
        except:
            return JsonResponse(data={'message': 'Произошла ошибка!'}, status=400)


class AddSourcesOfFundingView(UpdateView):
    model = Report
    form_class = AddSourcesOfFundingForm
    template_name = 'additional_pages/sources_of_funding_form.html'

    def post(self, request, *args, **kwargs):
        update_status(self.get_object().pk, request)
        return super(AddSourcesOfFundingView, self).post(request, *args, **kwargs)


class AddNewTag(View):
    template_name = 'add_new_tag.html'

    def post(self, request, *args, **kwargs):
        try:
            _ = Tag.objects.create(name=request.POST['name'])
            return JsonResponse(data={'message': f'Создан новый тег: {_.name}'}, status=200)
        except Exception as e:
            return JsonResponse(data={'message': f'Произошла ошибка: {type(e).__name__}, {e}'}, status=400)


class Feedback(View):
    def post(self, request, *args, **kwargs):
        try:
            thread = threading.Thread(target=send_email, args=(request.POST['message'], request.POST['user']))
            thread.start()
            return JsonResponse(data={'message': f'Сообщение отправлено'}, status=200)
        except Exception as e:
            return JsonResponse(data={'message': f'Произошла ошибка: {type(e).__name__}, {e}'}, status=400)


class ChangeWaitingStatus(View):
    def post(self, request, *args, **kwargs):
        report = Report.objects.get(pk=self.request.pk)
        if report.waiting:
            report.waiting = False

        else:
            report.waiting = True
            _ = WaitingStatusForUser.objects.create(
                sender=request.POST['sender'],receiver=request.POST['receiver'],report=report)


class DraftCreate(APIView):
    """Создание нового черновика"""
    @swagger_auto_schema(request_body=DraftCreateSerializer)
    def post(self, request):
        draft = DraftCreateSerializer(data=request.data)
        if draft.is_valid():
            draft.save(creator=request.user)
            return Response(draft.data, status=status.HTTP_201_CREATED)
        return Response(draft.errors, status=status.HTTP_400_BAD_REQUEST)

class DraftDetail(APIView):
    """Детали черновика"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]

    def get(self, request, pk):
        draft = Draft.objects.get(id=pk)
        serializer = DraftGetSerializer(draft)
        return Response(serializer.data)


class DraftListView(APIView):

    def get(self,request):
        queryset = Draft.custom_query.not_closed(user=request.user)
        serializer = DraftListSerializer(queryset, many=True)
        return Response(serializer.data)

class TagRUD(generics.RetrieveUpdateDestroyAPIView):
    """ Получение, обновление и удаление тега"""
    queryset = Tag.objects.all()
    serializer_class = TagsListSerializer
    # permission_classes = [IsSuperuserOrReadOnly]

class TagListAndCreate(generics.ListCreateAPIView):
    """ Получение списка тегов и создание нового тега"""
    queryset = Tag.objects.all()
    serializer_class = TagsListSerializer
    # permission_classes = [IsSuperuserOrReadOnly]
