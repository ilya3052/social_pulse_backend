from django.urls import path
from rest_framework_simplejwt.views import token_obtain_pair, token_refresh, token_verify

from social_auth.views import email_send_message_view, email_activation_view, restore_password_view, \
    send_restore_password_email, telegram_binding_view, telegram_callback_view, telegram_token_pair_view, \
    telegram_convert_token_view, vk_callback_view, vk_callback_user
from social_auth.views.token_view import token_blacklist_view

urlpatterns = [
    path('email/send/', email_send_message_view, name='email_send'),
    path('email/activate/', email_activation_view, name='email_activate'),

    path('password/send-email/', restore_password_view, name='password_send_email'),
    path('password/reset/', send_restore_password_email, name='password_restore'),

    path('tg/bind/', telegram_binding_view, name='tg_binding'),
    path('tg/callback/', telegram_callback_view, name='tg_callback'),
    path('tg/token/short/', telegram_token_pair_view, name='token_short'),
    path('tg/token/short/convert/', telegram_convert_token_view, name='token_convert'),

    path('vk/callback/', vk_callback_view, name='vk_callback'),
    path('vk/user/', vk_callback_user, name='vk_callback_user'),

    path('token/', token_obtain_pair, name='token_obtain_pair'),
    path('token/refresh/', token_refresh, name='token_refresh'),
    path('token/verify/', token_verify, name='token_verify'),
    path('token/blacklist/', token_blacklist_view, name='token_blacklist'),
]
