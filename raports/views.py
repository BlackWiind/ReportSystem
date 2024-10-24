from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django_filters.views import FilterView

from users.models import User, CuratorsGroup
from .models import Raport, Tag
from .form_utils import create_new_raport
from .forms import CuratorToDepartmentForm, CreateRaportForm
from .filters import RaportFilter
from raports.utils.utils import get_queryset_dependent_group, change_raport_status_by_request
from raports.utils.unloads import create_pdf_unloading


def temp_view(request):
    return render(request, 'raports/home.html')


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
    success_url = reverse_lazy('raports:home')

    def get_form(self, *args, **kwargs):
        form = super(RaportCreateView, self).get_form(*args, **kwargs)
        curator_group = CuratorsGroup.objects.get(name=self.request.user.department.curators_group)
        form.fields['tags'].queryset = Tag.objects.filter(curators_group=curator_group)
        return form

    def form_valid(self, form):
        print('form is valid')
        try:
            create_new_raport(self.request, form)
        except Exception as e:
            print('error')
            raise Exception(f"Create new raport error: {e.args} {e.__traceback__.tb_lineno}")
        else:
            return HttpResponseRedirect(self.success_url)

    def form_invalid(self, form):
        print('form invalid')
        print(form.errors.as_data())
        return super(RaportCreateView, self).form_invalid(form)


class RaportListView(FilterView):
    model = Raport
    template_name = 'raports/list.html'
    paginate_by = 10
    filterset_class = RaportFilter

    def get_queryset(self):
        return get_queryset_dependent_group(self.request.user)


class ArchiveListView(ListView):
    model = Raport
    template_name = 'raports/list.html'

    def get_queryset(self):
        return Raport.objects.filter(status__in=['rejected', 'done'])


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
    pass


class UpdateRaportStatusView(UpdateView):
    model = Raport
    template_name = 'raports/details.html'
    fields = ['status']

    def post(self, request, *args, **kwargs):
        my_object = self.get_object()
        resp = change_raport_status_by_request(request.user, my_object.pk, request.POST['status'])
        return JsonResponse(data={'response': resp})
