from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from users.models import Department
from .models import Report, Tag, SourcesOfFunding


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class FileFieldForm(forms.Form):
    file_field = MultipleFileField(required=False)


class CuratorToDepartmentForm(forms.ModelForm):
    name = forms.ModelMultipleChoiceField(
        queryset=Department.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('verbose name', is_stacked=False)
    )

    class Meta:
        model = Department
        fields = ['name']


class CreateReportForm(forms.ModelForm):

    class Meta:
        model = Report
        fields = [
            'text',
            'justification',
            'tags',
            'price',
            'one_time',
            'files',
            'sign',
        ]
        widgets = {'sign': forms.HiddenInput()}

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    files = MultipleFileField(required=False)

    def main_group(self):
        return [field for field in self if field.name in ['text',
                                                          'justification',
                                                          'price',
                                                          'files',
                                                          'sign',]]

    def checkbox_group(self):
        return [field for field in self if field.name in ['tags',]]


class AddFilesAndNewPriceForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['files', 'price', ]

    files = MultipleFileField(required=False, label='Прикреплённые файлы')


class AddSourcesOfFundingForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['sources_of_funding', ]

        sources_of_funding = forms.ModelMultipleChoiceField(
            queryset=SourcesOfFunding.objects.all(),
            widget=forms.CheckboxSelectMultiple
        )
