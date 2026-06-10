from rest_framework.permissions import BasePermission

from social_auth.models import ResetPassword
from users.models import CustomUser


class IsAuthenticatedOrHasResetToken(BasePermission):
    def has_permission(self, request, view):
        if token := request.data.get('token'):
            token_instance = ResetPassword.objects.get(token=token)
            user = CustomUser.objects.get(email=token_instance.email)
            user.set_unusable_password()
            view.reset_user = user
            del request.data['token']
            return True
        return bool(request.user and request.user.is_authenticated)