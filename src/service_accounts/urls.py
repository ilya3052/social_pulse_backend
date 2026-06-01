from django.urls import path

from service_accounts.views import ServiceAccountsView, ServiceAccountActivateView

urlpatterns = [
    path('all/', ServiceAccountsView.as_view({"get": "list"}), name='get-service-accounts-info'),
    path('activate/<int:account_id>', ServiceAccountActivateView.as_view(), name='activate-service-account'),
    path('<int:pk>', ServiceAccountsView.as_view({"delete": "destroy"}), name='delete-service-account'),
    path('', ServiceAccountsView.as_view({"post": "create"}), name='create-service-account'),
]
