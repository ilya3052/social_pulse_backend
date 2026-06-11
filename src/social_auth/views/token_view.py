from rest_framework_simplejwt.views import TokenBlacklistView

from social_auth.models import VKTokens


class _TokenBlacklistView(TokenBlacklistView):
    def post(self, request, *args, **kwargs):
        refresh = request.data.get('refresh')
        if refresh:
            try:
                from rest_framework_simplejwt.tokens import RefreshToken
                token = RefreshToken(refresh)
                user_id = token.get('user_id')
                VKTokens.objects.filter(user_id=user_id).delete()
            except Exception:
                pass
        return super().post(request, *args, **kwargs)

token_blacklist_view = _TokenBlacklistView.as_view()