from django.urls import path

from users.views import user_api_registration, user_api_view, unbind_social_view, user_social_data, user_set_password, \
    user_change_password

urlpatterns = [
    path('register/', user_api_registration, name='register'),

    path(r'me/', user_api_view, name='me'),
    path('unbind-social/', user_change_password, name='unbind_social'),
    path('change-password/', user_set_password, name='change_password'),
    path('set-password/', user_social_data, name='set_password'),
    path('get-social/', unbind_social_view, name='user-social-data'),
]
