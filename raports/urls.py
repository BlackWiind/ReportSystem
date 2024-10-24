from django.urls import path
from . import views

app_name = 'raports'

urlpatterns = [
    path('home/', views.temp_view, name='home'),
    path('admin_page/', views.admin_page, name='admin_page'),
    path('create_raport/', views.RaportCreateView.as_view(), name='create_raport'),
    path('list/', views.RaportListView.as_view(), name='list'),
    path('details/<int:pk>/', views.RaportDetailView.as_view(), name='details'),
    path('update_raport/<int:pk>/', views.UpdateRaportStatusView.as_view(), name='update_raport'),
    path('curators_modal/', views.get_curator_groups, name='curators_modal'),
    path('change_curators_group/<int:pk>/', views.change_curators_group, name='change_curators_group'),
    path('archive/', views.ArchiveListView.as_view(), name='archive'),
    path('download_pdf/<int:pk>/', views.download_pdf_report, name='download_pdf'),
]
