import threading

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView
from django_filters.views import FilterView

from users.models import User, CuratorsGroup
from .mail import send_email
from .models import Raport, Tag, Files
from raports.utils.form_utils import create_new_raport
from .forms import CreateRaportForm, AddFilesAndNewPriceForm, AddSourcesOfFundingForm
from .filters import RaportFilter
from raports.utils.utils import get_queryset_dependent_group, update_status
from raports.utils.unloads import create_pdf_unloading


class RaportCreateView(CreateView):
    form_class = CreateRaportForm
    template_name = 'raports/create_raport.html'
    success_url = reverse_lazy('raports:list')

    # def get_form(self, *args, **kwargs):
    #     form = super(RaportCreateView, self).get_form(*args, **kwargs)
    #     curator_group = CuratorsGroup.objects.get(name=self.request.user.department.curators_group)
    #     form.fields['tags'].queryset = Tag.objects.filter(curators_group=curator_group)
    #     return form

    def form_valid(self, form):
        try:
            create_new_raport(self.request, form)
        except Exception as e:
            raise Exception(f"Create new raport error: {e.args} {e.__traceback__.tb_lineno}")
        else:
            return HttpResponseRedirect(self.success_url)

    def form_invalid(self, form):
        return super(RaportCreateView, self).form_invalid(form)


class RaportListView(FilterView):
    model = Raport
    template_name = 'raports/list.html'
    paginate_by = 5
    filterset_class = RaportFilter

    def get_queryset(self):
        return get_queryset_dependent_group(self.request.user)


class ArchiveListView(FilterView):
    model = Raport
    template_name = 'raports/list.html'
    paginate_by = 5
    filterset_class = RaportFilter

    def get_queryset(self):
        return Raport.objects.filter(status__status__in=['rejected', 'done'])


class RaportDetailView(DetailView):
    model = Raport
    template_name = 'raports/details.html'


def get_curator_groups(request):
    if request.method == 'GET':
        context = {'groups': CuratorsGroup.objects.all()}
        return render(request, 'additional_pages/modal_of_curator_groups.html', context)


def download_pdf_report(request, pk):
    return create_pdf_unloading(pk)


def change_curators_group(request, pk):
    if request.method == 'POST':
        _ = Raport.objects.filter(pk=pk).update(curators_group=request.POST['new_group'])
        return JsonResponse(data={'message': 'Рапорт успешно обновлён'})


def get_purchasing_specialist(request):
    if request.method == 'GET':
        context = {'purchasers': User.objects.filter(groups__name='purchasing_specialist')}
        return render(request, 'additional_pages/modal_of_purchasing_specialists.html', context)


class UpdateRaportStatusView(UpdateView):
    model = Raport
    template_name = 'raports/details.html'
    fields = ['status']

    def post(self, request, *args, **kwargs):
        try:
            update_status(self.get_object().pk, request)
            return JsonResponse(data={'message': 'ok'}, status=200)
        except:
            return JsonResponse(data={'message': 'Произошла ошибка!'}, status=400)


class AddFilesToExistedRaport(UpdateView):
    model = Raport
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
    model = Raport
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
