from rest_framework import serializers

from .models import Report, Tag, History, WaitingStatusForUser, Files
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

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ('id', 'file')

class ReportPatchSerializer(serializers.ModelSerializer):
    uploaded_files = serializers.ListField(
        child=serializers.FileField(max_length=100000, allow_empty_file=True, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = Report
        exclude =('parents', 'sign', 'curators_group')

    def update(self, instance, validated_data):
        uploaded_files = validated_data.pop('uploaded_files', [])

        # Обновляем остальные поля
        instance = super().update(instance, validated_data)

        # Добавляем новые файлы
        for file in uploaded_files:
            new_file = Files.objects.create(file=file)
            instance.files.add(new_file)

        return instance

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

