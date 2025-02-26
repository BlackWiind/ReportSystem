from rest_framework import serializers

from .models import Report, Tag
from users.serializers import StatusesSerializer

class TagsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class DraftCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Report
        fields = ('text', 'justification', 'price', 'tags',)


class DraftListSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)

    class Meta:
        model = Report
        fields = ('text', 'justification', 'price', 'tags',)


class ReportCreateSerializer(serializers.ModelSerializer):
    """ Создание нового рапорта"""

    class Meta:
        model = Report
        fields = ('text', 'justification', 'price', 'one_time', 'tags', 'responsible', 'parents',)


class ReportRetrieveUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)
    status = StatusesSerializer(read_only=True)
    history = serializers.SlugRelatedField(slug_field='action__verbose_name', read_only=True, many=True)
    responsible = serializers.SlugRelatedField(slug_field='last_name', read_only=True)
    parents = serializers.HyperlinkedRelatedField(lookup_field='pk', many=True, read_only=True, view_name='reports:report-detail')

    class Meta:
        model = Report
        exclude =('sign', 'draft', 'curators_group')

class ReportListSerializer(serializers.ModelSerializer):
    """ Список рапортов"""

    responsible = serializers.SlugRelatedField(slug_field='last_name', read_only=True)
    tags = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)
    # history = serializers.SlugRelatedField(slug_field='action__verbose_name', read_only=True, many=True)

    class Meta:
        model = Report
        fields = ('id', 'responsible', 'text', 'price', 'tags', 'assigned_purchasing_specialist', 'status',)