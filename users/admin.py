from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Department, CuratorsGroup


class CustomUserAdmin(UserAdmin):
    class Media:
        css = {
            'all': ('css/admin/my_own.css',)
        }

    list_of_fields = (
        'id',
        'username',
        'last_name',
        'first_name',
        'surname',
        'department',
        'curators_group',
        'job_title',
    )
    list_display = list_of_fields

    list_display_links = list_of_fields

    search_fields = (
        'id',
        'username',
        'last_name',
        'first_name',
        'surname',
        'department__name',
        'job_title',
    )
    list_filter = ['department__name', ]

    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Custom Field Heading',
            {
                'fields': (
                    'surname',
                    'department',
                    'curators_group',
                    'job_title',
                )
            }
        )
    )


class DepartmentAdmin(admin.ModelAdmin):
    list_of_fields = ('id', 'name')
    list_display = list_of_fields
    list_display_links = list_of_fields


class CuratorsGroupAdmin(admin.ModelAdmin):
    list_of_fields = ('id', 'name')
    list_display = list_of_fields
    list_display_links = list_of_fields


admin.site.register(User, CustomUserAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(CuratorsGroup, CuratorsGroupAdmin)
