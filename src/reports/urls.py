from django.urls import path

from reports.views import AdminReportPDFView, GroupReportsView, CompareGroupReportView, UserReportsView

urlpatterns = [
    path('', UserReportsView.as_view({"get": "list"}), name='reports'),
    path('admin/', AdminReportPDFView.as_view(), name='admin_report'),
    path('group/<int:pk>/', GroupReportsView.as_view(), name='group_report'),
    path('compare/', CompareGroupReportView.as_view(), name='compare_report'),
]
