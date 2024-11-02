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
    list_of_fields = ('id', 'creator',  'price', 'one_time',)
    list_display = list_of_fields
    list_display_links = list_of_fields

    search_fields = (
        'id',
        'creator__last_name',
        'one_time',
    )

    list_filter = ['creator__last_name',  'one_time', ]


class FilesAdmin(admin.ModelAdmin):
    list_of_fields = ('id', 'file', )
    list_display = list_of_fields
    list_display_links = list_of_fields


class HistoryAdmin(admin.ModelAdmin):
    list_of_fields = ('id','action', 'user', )
    list_display = list_of_fields
    list_display_links = list_of_fields


admin.site.register(Tag, TagAdmin)
admin.site.register(Raport, RaportAdmin)
admin.site.register(Files, FilesAdmin)
admin.site.register(History, HistoryAdmin)
