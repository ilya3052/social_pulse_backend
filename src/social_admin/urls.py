from django.urls import path

from social_admin.views import summary_admin_panel_view

urlpatterns = [
    path('summary/', summary_admin_panel_view, name='summary-admin-panel'),
]
