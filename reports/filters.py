import django_filters
from django_filters import rest_framework as filters
from django_filters import DateFromToRangeFilter, BooleanFilter
from django_filters.widgets import DateRangeWidget

from .models import Report


class ReportFilter(filters.FilterSet):


    date_create = DateFromToRangeFilter(
        lookup_expr=('icontains'),
        widget=django_filters.widgets.RangeWidget(
            attrs={'type':'date'}
        )
    )
    my_reports = BooleanFilter(label='Требующие внимания')


    class Meta:
        model = Report
        fields = {'creator': ['exact'],
                  'responsible': ['exact'],
                  'creator__department': ['exact'],
                  'tags': ['exact'],
                  'date_create': ['exact'],
                  'one_time': ['exact'],
                  'draft': ['exact'],
                  }

    @property
    def qs(self):
        parent = super().qs
        statuses = self.request.user.custom_permissions.statuses.all().values_list('status', flat=True)
        my_reports = self.request.GET.get('my_reports', None)
        if my_reports:
            return parent.filter(status__status__in=statuses)
        return parent