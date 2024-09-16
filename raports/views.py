from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from users.models import User, CuratorsGroup
from .form_utils import create_new_raport
from .forms import CuratorToDepartmentForm, CreateRaportForm, FileFieldForm
from .models import Raport, Tag


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

    def get_context_data(self, **kwargs):
        context = super(RaportCreateView, self).get_context_data(**kwargs)
        context['file_upload'] = FileFieldForm()
        return context

    def get_form(self, *args, **kwargs):
        form = super(RaportCreateView, self).get_form(*args, **kwargs)
        curator_group = CuratorsGroup.objects.get(name=self.request.user.department.curators_group)
        form.fields['tags'].queryset = Tag.objects.filter(curators_group=curator_group)
        return form

    def form_valid(self, form):
        # new_raport = Raport.objects.create(
        #     creator=self.request.user,
        #     text=form.cleaned_data['text'],
        #     justification=form.cleaned_data['justification'],
        #     price=form.cleaned_data['price'],
        # )
        # for tag in form.cleaned_data['tags']:
        #     new_raport.tags.add(tag)
        # new_raport.save()
        if create_new_raport(self.request, form):
            print('Hey-ho')
        return HttpResponseRedirect(self.success_url)
