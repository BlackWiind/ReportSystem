from rest_framework import serializers

from .models import Report, Tag, History, WaitingStatusForUser
from users.serializers import StatusesSerializer, CuratorsGroupSerializer, UserSerializer, UserShortDataSerializer


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
        fields = ('id', 'text', 'justification', 'price', 'tags', 'creator', 'history','date_create',)


class ReportCreateSerializer(serializers.ModelSerializer):
    """ Создание нового рапорта"""

    class Meta:
        model = Report
        fields = ('text', 'justification', 'price', 'one_time', 'tags', 'responsible', 'parents',)


class ReportRetrieveUpdateSerializer(serializers.ModelSerializer):
    creator = UserShortDataSerializer(read_only=True)
    assigned_purchasing_specialist = UserShortDataSerializer(read_only=True)
    responsible = UserShortDataSerializer(read_only=True)
    tags = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)
    status = StatusesSerializer(read_only=True)
    history = HistorySerializer(read_only=True, many=True)
    parents = serializers.HyperlinkedRelatedField(lookup_field='pk', many=True, read_only=True, view_name='reports:report-detail')

    class Meta:
        model = Report
        exclude =('sign', 'curators_group')

class ReportPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        exclude =('parents', 'sign', 'curators_group')

class ReportListSerializer(serializers.ModelSerializer):
    """ Список рапортов"""

    responsible = UserShortDataSerializer(read_only=True)
    tags = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)
    status = serializers.SlugRelatedField(slug_field='visible_name', read_only=True)
    history = HistorySerializer(read_only=True, many=True)
    creator = UserShortDataSerializer(read_only=True)
    assigned_purchasing_specialist = UserShortDataSerializer(read_only=True)

    class Meta:
        model = Report
        fields = ('id', 'creator', 'responsible', 'text',
                  'price', 'tags', 'assigned_purchasing_specialist',
                  'status','history', 'date_create', 'one_time', 'waiting', 'closed', 'draft',)


class HistoryUpdateSerializer(serializers.ModelSerializer):
    waiting = serializers.BooleanField(required=False)
    class Meta:
        model = History
        fields = ('text', 'waiting',)


class WaitingStatusForUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = WaitingStatusForUser
        fields = ('report',)

