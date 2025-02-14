from rest_framework import serializers

from .models import Report, Tag

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

    # tags = TagsListSerializer(many=True)

    class Meta:
        model = Report
        fields = ('text', 'justification', 'price', 'one_time', 'tags', 'responsible', 'parents',)


class ReportRetrieveUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Report
        # fields = (
        #     'creator',
        #     'text',
        #     'justification',
        #     'price',
        #     'one_time',
        #     'tags',
        #     'date_create',
        #     'status',
        #     'responsible',
        #     'files',
        #     'print_form',
        #     'parents',)
        exclude =('sign', 'draft', 'curators_group')

class ReportListSerializer(serializers.ModelSerializer):
    """ Список рапортов"""

    responsible = serializers.SlugRelatedField(slug_field='last_name', read_only=True)
    tags = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)
    history = serializers.SlugRelatedField(slug_field='action__verbose_name', read_only=True, many=True)

    class Meta:
        model = Report
        fields = ('responsible', 'text', 'price', 'tags', 'assigned_purchasing_specialist', 'status', 'history', )