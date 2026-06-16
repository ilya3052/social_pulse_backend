from django.urls import path

from users.views import user_api_registration, user_api_view, unbind_social_view, user_social_data, user_set_password, \
    user_change_password

urlpatterns = [
    path('register/', user_api_registration, name='register'),

    path(r'me/', user_api_view, name='me'),
    path('unbind-social/', unbind_social_view, name='unbind_social'),
    path('change-password/', user_change_password, name='change_password'),
    path('set-password/', user_set_password, name='set_password'),
    path('get-social/', user_social_data, name='user-social-data'),
]
