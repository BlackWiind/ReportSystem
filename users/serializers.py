from rest_framework import serializers

from .models import User, CuratorsGroup, Department, CustomPermissions, Statuses, Links, PossibleActions

class StatusesSerializer(serializers.ModelSerializer):
    """Сериалайзер для доступных статусов"""

    class Meta:
        model = Statuses
        fields = ('status', 'verbose_name',)

class PossibleActionsSerializer(serializers.ModelSerializer):
    """Сериалайзаер для доступных действий с рапортом"""

    class Meta:
        model = PossibleActions
        fields = ('name', 'visible_name',)

class LinksSerializer(serializers.ModelSerializer):
    """Сериалайзер для доступных ссылок"""

    class Meta:
        model = Links
        fields = ('name', 'link',)


class CuratorsGroupSerializer(serializers.ModelSerializer):
    """ Сериалайзер для курируемых групп"""

    class Meta:
        model = CuratorsGroup
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    """Сериалайзер для отделений"""

    curators_group = CuratorsGroupSerializer(read_only=True)

    class Meta:
        model = Department
        fields = ('name', 'curators_group',)

class CustomPermissionsSerializer(serializers.ModelSerializer):
    """Сериалайзер для групп доступа"""
    statuses = StatusesSerializer(many=True, read_only=True)
    possible_actions = PossibleActionsSerializer(many=True, read_only=True)
    links = LinksSerializer(many=True, read_only=True)

    class Meta:
        model = CustomPermissions
        fields = ('name', 'description', 'statuses', 'possible_actions', 'links',)


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер для пользователей"""
    department = DepartmentSerializer(read_only=True)
    curators_group = CuratorsGroupSerializer(read_only=True)
    custom_permissions = CustomPermissionsSerializer(read_only=True)

    class Meta:
        model = User
        exclude = ['password', 'last_login', 'is_superuser',
                   'email', 'is_staff', 'is_active', 'date_joined', 'user_permissions']

class UserShortDataSerializer(serializers.ModelSerializer):
    """Сериалайзер для краткой информации о пользователях"""

    class Meta:
        model = User
        fields = ['id','first_name', 'last_name', 'surname',
                   'department', 'job_title',]
