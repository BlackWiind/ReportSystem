import django_filters
from django_filters import DateFromToRangeFilter
from django_filters.widgets import DateRangeWidget

from users.models import CuratorsGroup
from .models import Raport, Tag


class RaportFilter(django_filters.FilterSet):

    def get_tags_queryset(self):
        pass
    date_create = DateFromToRangeFilter(
        lookup_expr=('icontains'),
        widget=django_filters.widgets.RangeWidget(
            attrs={'type':'date'}
        )
    )

    # tags = django_filters.ChoiceFilter(queryset=get_tags_queryset)

    class Meta:
        model = Raport
        fields = {'creator': ['exact'],
                  'creator__department': ['exact'],
                  'tags': ['exact'],
                  'date_create': ['exact'],
                  'one_time': ['exact'],
                  }
