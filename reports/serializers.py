from rest_framework import serializers

from .models import Draft, Report, Tag

class TagsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class DraftListSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)

    class Meta:
        model = Draft
        fields = ('text', 'price', 'tags', 'date_create',)


class DraftCreateSerializer(serializers.ModelSerializer):
    """Создание черновика"""

    class Meta:
        model = Draft
        fields = ('text', 'justification', 'price', 'one_time', 'tags',)

class DraftGetSerializer(serializers.ModelSerializer):
    """Детали одного черновика"""

    tags = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)

    class Meta:
        model = Draft
        fields = ('creator', 'text', 'justification', 'price', 'one_time', 'tags', 'date_create',)

class ReportCreateSerializer(serializers.ModelSerializer):
    """ Создание нового рапорта"""

    class Mete:
        model = Report
        fields = ('text', 'justification', 'price', 'one_time', 'tags', 'responsible', 'parents',)