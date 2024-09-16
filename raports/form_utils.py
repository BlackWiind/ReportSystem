from raports.forms import CreateRaportForm, FileFieldForm
from raports.models import Raport, Files


def create_new_raport(request, form):
    new_raport = Raport.objects.create(
        creator=request.user,
        text=form.cleaned_data['text'],
        justification=form.cleaned_data['justification'],
        price=form.cleaned_data['price'],
        curators_group=request.user.department.curators_group,
    )
    for tag in form.cleaned_data['tags']:
        new_raport.tags.add(tag)
    new_raport.save()
    new_files_upload(request, Raport.objects.latest('id'))
    return True


def new_files_upload(request, raport):
    form = FileFieldForm(request.POST, request.FILES)
    if form.is_valid():
        try:
            files = form.cleaned_data['file_field']
            for file in files:
                new_file = Files(file=file, raport=raport)
                new_file.save()
        except Exception as e:
            raise Exception(f"File upload form save error: {e.args} {e.__traceback__.tb_lineno}")
