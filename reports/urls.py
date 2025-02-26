from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # path('create_report/', views.ReportCreateView.as_view(), name='create_report'),
    # path('list/', views.HomePage.as_view(), name='list'),
    # path('details/<int:pk>/', views.ReportDetailView.as_view(), name='details'),
    # path('update_report/<int:pk>/', views.UpdateReportStatusView.as_view(), name='update_report'),
    # path('curators_modal/', views.get_curator_groups, name='curators_modal'),
    # path('purchasers_modal/', views.get_purchasing_specialist, name='purchasers_modal'),
    # path('change_curators_group/<int:pk>/', views.change_curators_group, name='change_curators_group'),
    # path('archive/', views.ArchiveListView.as_view(), name='archive'),
    # path('download_pdf/<int:pk>/', views.download_pdf_report, name='download_pdf'),
    # path('sources_of_funding_form/<int:pk>/', views.AddSourcesOfFundingView.as_view(), name='sources_of_funding_form'),
    # path('add_files_form/<int:pk>/', views.AddFilesToExistedReport.as_view(), name='add_files_form'),
    # path('add_new_tag/', views.AddNewTag.as_view(), name='add_new_tag'),
    # path('feedback/', views.Feedback.as_view(), name='feedback'),

    path('draft/create', views.DraftCreate.as_view(), name='new_draft'),
    path('draft/list', views.DraftList.as_view(), name='draft_list'),

    path('tags/list-or-create', views.TagListAndCreate.as_view(), name='tags_list_or_create'),
    path('tags/<int:pk>', views.TagRUD.as_view(), name='tag'),

    path('reports/list', views.ReportList.as_view(), name='reports_list'),
    path('reports/create', views.Report2Create.as_view(), name='report'),
    path('reports/retrieve-update/<int:pk>', views.ReportRetrieveUpdate.as_view(), name='report-detail')
]
