from reports.models import Report, Files, History
from users.models import Statuses


def create_new_report(request, form):
    new_report = Report.objects.create(
        creator=request.user,
        text=form.cleaned_data['text'],
        justification=form.cleaned_data['justification'],
        price=form.cleaned_data['price'],
        curators_group=request.user.department.curators_group,
        sign=form.cleaned_data['sign'],
    )
    new_report.tags.add(*form.cleaned_data['tags'])
    for file in form.cleaned_data['files']:
        new_report.files.add(Files.objects.create(file=file).pk)
    new_report.history.add(add_history_record(request.user, Statuses.objects.get(status='created')).pk)
    new_report.save()
    print('Good')


def add_history_record(user, action):
    return History.objects.create(user=user, action=action)

