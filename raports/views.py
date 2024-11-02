import json
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from django_filters.views import FilterView

from users.models import User, CuratorsGroup
from .models import Raport, Tag, History
from .form_utils import create_new_raport
from .forms import CuratorToDepartmentForm, CreateRaportForm
from .filters import RaportFilter
from raports.utils.utils import get_queryset_dependent_group, ajax_decoder
from raports.utils.unloads import create_pdf_unloading


def admin_page(request):
    curators_set = User.objects.filter(groups__name='curator')
    context = {
        'curators_set': curators_set,
        'form': CuratorToDepartmentForm
    }
    return render(request, 'raports/admin_page.html', context=context)


class RaportCreateView(CreateView):
    form_class = CreateRaportForm
    template_name = 'raports/create_raport.html'
    success_url = reverse_lazy('raports:list')

    def get_form(self, *args, **kwargs):
        form = super(RaportCreateView, self).get_form(*args, **kwargs)
        curator_group = CuratorsGroup.objects.get(name=self.request.user.department.curators_group)
        form.fields['tags'].queryset = Tag.objects.filter(curators_group=curator_group)
        return form

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
        print(11111)
        try:
            raport = Raport.objects.filter(pk=self.get_object().pk)
            raport.update(**ajax_decoder(request))
            for q in raport:
                q.history.create(user=request.user, action=q.status)
            return JsonResponse(data={'message': 'ok'}, status=200)
        except:
            return JsonResponse(data={'message': 'huita'}, status=400)
