from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('create_report/', views.ReportCreateView.as_view(), name='create_report'),
    path('list/', views.ReportListView.as_view(), name='list'),
    path('details/<int:pk>/', views.ReportDetailView.as_view(), name='details'),
    path('update_report/<int:pk>/', views.UpdateReportStatusView.as_view(), name='update_report'),
    path('curators_modal/', views.get_curator_groups, name='curators_modal'),
    path('purchasers_modal/', views.get_purchasing_specialist, name='purchasers_modal'),
    path('change_curators_group/<int:pk>/', views.change_curators_group, name='change_curators_group'),
    path('archive/', views.ArchiveListView.as_view(), name='archive'),
    path('download_pdf/<int:pk>/', views.download_pdf_report, name='download_pdf'),
    path('sources_of_funding_form/<int:pk>/', views.AddSourcesOfFundingView.as_view(), name='sources_of_funding_form'),
    path('add_files_form/<int:pk>/', views.AddFilesToExistedReport.as_view(), name='add_files_form'),
    path('add_new_tag/', views.AddNewTag.as_view(), name='add_new_tag'),
    path('feedback/', views.Feedback.as_view(), name='feedback'),

    path('api/new_draft/', views.DraftCreate.as_view(), name='new_draft'),
    path('api/details_draft/<int:pk>/', views.DraftDetail.as_view()),
    path('api/draft-list/', views.DraftListView.as_view(), name='draft_list'),
    path('api/tags-list', views.TagsListAndCreate.as_view(), name='tags_list'),
]
