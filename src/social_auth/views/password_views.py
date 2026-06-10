from smtplib import SMTPException

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from social_auth.models import ResetPassword
from social_auth.services import send_email
from social_auth.utils import prepare_message, generate_short_token
from users.models import CustomUser


class RestorePasswordView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        token = request.GET.dict().get('token')
        token_instance = ResetPassword.objects.get(token=token)
        if token_instance.expires_at < timezone.now():
            return Response({'error': 'expired'}, status=status.HTTP_403_FORBIDDEN)
        user = CustomUser.objects.get(email=token_instance.email)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_200_OK)


class SendRestorePasswordEmail(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        token = generate_short_token()

        reset_password_instance = ResetPassword.objects.filter(email=email).first()
        if reset_password_instance:
            reset_password_instance.delete()

        ResetPassword.objects.create(email=email, token=token)
        message = prepare_message(token, 'reset')
        try:
            send_email('Сброс пароля', message, email)
            return Response(status=status.HTTP_200_OK)
        except SMTPException as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)