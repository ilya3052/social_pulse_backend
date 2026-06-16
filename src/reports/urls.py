from django.urls import path

from reports.views import user_reports_view, admin_report_pdf_view, group_reports_view, compare_groups_view

urlpatterns = [
    path('', user_reports_view, name='reports'),
    path('admin/', admin_report_pdf_view, name='admin_report'),
    path('group/<int:pk>/', group_reports_view, name='group_report'),
    path('compare/', compare_groups_view, name='compare_report'),
]
