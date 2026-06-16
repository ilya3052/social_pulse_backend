from django.urls import path

from service_accounts.views import service_accounts_list_view, service_account_activate_view, \
    service_account_update_delete_view, service_account_retrieve_view, service_account_create_view

urlpatterns = [
    path('all/', service_accounts_list_view, name='get-service-accounts-info'),
    path('activate/<int:account_id>', service_account_activate_view, name='activate-service-account'),
    path('<int:pk>', service_account_update_delete_view, name='update-delete-service-account'),
    path('<str:platform>', service_account_retrieve_view, name='get-service-account'),
    path('', service_account_create_view, name='create-service-account'),
]
