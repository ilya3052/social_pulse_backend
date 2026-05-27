from django.urls import path

from reports.views import AdminReportPDFView, GroupReportsView

urlpatterns = [
    path('admin/', AdminReportPDFView.as_view(), name='admin_report'),
    path('group/<int:pk>/', GroupReportsView.as_view(), name='group_report'),
]