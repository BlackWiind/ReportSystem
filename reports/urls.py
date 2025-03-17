from django.urls import path
from . import views
from . import api

app_name = 'reports'

urlpatterns = [
    path('draft/list-and-create', api.DraftListAndCreate.as_view(), name='new_draft'),

    path('tags/list-or-create', api.TagListAndCreate.as_view(), name='tags_list_or_create'),
    path('tags/<int:pk>', api.TagRUD.as_view(), name='tag'),

    path('reports/list', api.ReportList.as_view(), name='reports_list'),
    path('reports/create', api.ReportCreate.as_view(), name='report'),
    path('reports/retrieve-update/<int:pk>', api.ReportRetrieveUpdate.as_view(), name='report-detail'),

    path('approve/<int:pk>', api.ReportApproveClose.as_view({'patch': 'report_approve'})),
    path('close/<int:pk>', api.ReportApproveClose.as_view({'patch': 'report_close'})),
    path('waiting/<int:pk>', api.ReportApproveClose.as_view({'patch': 'report_freeze'})),

    path('feedback/', api.Feedback.as_view()),
    path('canishutdownwaiting/', api.CanIShutDownWaiting.as_view())
]
