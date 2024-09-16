from django.contrib import admin

from .models import Tag, Raport, History, Files


class TagAdmin(admin.ModelAdmin):
    list_of_fields = ('id', 'name', 'curators_group')
    list_display = list_of_fields
    list_display_links = list_of_fields

    search_fields = (
        'id',
        'name',
        'curators_group__name',
    )

    list_filter = ['curators_group__name', ]


class RaportAdmin(admin.ModelAdmin):
    list_of_fields = ('id', 'creator', 'status', 'price', 'one_time',)
    list_display = list_of_fields
    list_display_links = list_of_fields

    search_fields = (
        'id',
        'status',
        'creator__last_name',
        'one_time',
    )

    list_filter = ['creator__last_name', 'status', 'one_time', ]


class FilesAdmin(admin.ModelAdmin):
    list_of_fields = ('id', 'file', 'raport',)
    list_display = list_of_fields
    list_display_links = list_of_fields


admin.site.register(Tag, TagAdmin)
admin.site.register(Raport, RaportAdmin)
admin.site.register(Files, FilesAdmin)
