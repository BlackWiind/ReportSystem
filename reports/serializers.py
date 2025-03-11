from rest_framework import serializers

from .models import Report, Tag, History
from users.serializers import StatusesSerializer, CuratorsGroupSerializer, UserSerializer


class TagsSerializer(serializers.ModelSerializer):
    group = CuratorsGroupSerializer(read_only=True)
    class Meta:
        model = Tag
        fields = '__all__'

class HistorySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = History
        fields = '__all__'



class DraftSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    tags = TagsSerializer
    history = HistorySerializer(read_only=True, many=True)

    class Meta:
        model = Report
        fields = ('text', 'justification', 'price', 'tags', 'creator', 'history',)



class ReportCreateSerializer(serializers.ModelSerializer):
    """ Создание нового рапорта"""

    class Meta:
        model = Report
        fields = ('text', 'justification', 'price', 'one_time', 'tags', 'responsible', 'parents',)


class ReportRetrieveUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)
    status = StatusesSerializer(read_only=True)
    history = HistorySerializer(read_only=True, many=True)
    responsible = serializers.SlugRelatedField(slug_field='last_name', read_only=True)
    parents = serializers.HyperlinkedRelatedField(lookup_field='pk', many=True, read_only=True, view_name='reports:report-detail')

    class Meta:
        model = Report
        exclude =('sign', 'draft', 'curators_group')

class ReportListSerializer(serializers.ModelSerializer):
    """ Список рапортов"""

    responsible = UserSerializer(read_only=True)
    tags = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)
    history = HistorySerializer(read_only=True, many=True)
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Report
        fields = ('id', 'creator', 'responsible', 'text', 'price', 'tags', 'assigned_purchasing_specialist', 'status','history',)


class HistoryUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = History
        fields = ('text', )
