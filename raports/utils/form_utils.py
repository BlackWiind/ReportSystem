from raports.models import Raport, Files, History
from users.models import Statuses


def create_new_raport(request, form):
    new_raport = Raport.objects.create(
        creator=request.user,
        text=form.cleaned_data['text'],
        justification=form.cleaned_data['justification'],
        price=form.cleaned_data['price'],
        curators_group=request.user.department.curators_group,
        sign=form.cleaned_data['sign'],
    )
    new_raport.tags.add(*form.cleaned_data['tags'])
    for file in form.cleaned_data['files']:
        new_raport.files.add(Files.objects.create(file=file).pk)
    new_raport.history.add(add_history_record(request.user, Statuses.objects.get(status='created')).pk)
    new_raport.save()
    print('Good')


def add_history_record(user, action):
    return History.objects.create(user=user, action=action)

