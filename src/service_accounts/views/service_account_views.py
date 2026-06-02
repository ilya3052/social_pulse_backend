import os
from heapq import heapify, heappop, heappush
from secrets import token_hex

from django.db.models import Count, Q
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from service_accounts.models import ServiceAccount, OneTimeToken, ServiceAccountData
from service_accounts.permissions import ReadOnly
from service_accounts.serializers import ServiceAccountSerializer
from social_entities.models import Group


class ServiceAccountsView(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action == 'retrieve':
            permission_classes = [IsAuthenticated]
        elif self.action in ('list', 'create', 'partial_update', 'destroy', 'get_with_groups'):
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [ReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return (ServiceAccount.objects
                .select_related('data')
                .select_related('platform')
                .prefetch_related('groups')
                .all())

    pagination_class = None

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        queryset = self.get_queryset().filter(~Q(id=self.kwargs['pk']) & Q(platform=instance.platform))

        account_groups = instance.groups.all()
        accounts_dict = {}
        accounts_heap = []

        for acc in queryset:
            _id = acc.id
            accounts_heap.append([acc.groups.count(), _id])
            accounts_dict[_id] = acc

        heapify(accounts_heap)
        groups_to_update = []
        for group in account_groups:
            load, account_id = heappop(accounts_heap)
            account_to_link = accounts_dict.get(account_id)
            group.service_account = account_to_link
            groups_to_update.append(group)
            heappush(accounts_heap, [load + 1, account_id])

        Group.objects.bulk_update(groups_to_update, ['service_account'])

        account_data: ServiceAccountData = instance.data
        if session_path := account_data.session_path:
            if os.path.exists(session_path):
                os.remove(session_path)
        return super().destroy(request, *args, *kwargs)

    def retrieve(self, request, *args, **kwargs):
        account = (
            ServiceAccount.objects.filter(platform__alias=self.kwargs.get('platform'))
            .prefetch_related('groups')
            .annotate(
                groups_count=Count('groups')
            )
            .order_by('groups_count', 'name')
        ).first()

        if not account:
            return Response({"msg": "Сервисный аккаунт не найден"}, status=status.HTTP_404_NOT_FOUND)

        context = {
            'exclude_fields': [
                'platform_id', 'data', 'groups', 'groups_count', 'app_id'
            ]
        }

        serializer = ServiceAccountSerializer(account, context=context)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        accounts = (
            ServiceAccount.objects.all()
            .annotate(
                groups_count=Count('groups')
            )
        )

        context = {
            'exclude_fields': [
                'data', 'groups', 'platform_id', 'app_id'
            ]
        }
        from social_entities.services import get_group_aggregated_info
        group_data = get_group_aggregated_info()
        serializer = ServiceAccountSerializer(accounts, many=True, context=context)
        return Response(
            {"data": serializer.data, "total_group_count": group_data.get('vk_count') + group_data.get('tg_count')},
            status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        instance = ServiceAccount.objects.get(pk=self.kwargs.get('pk'))
        if not instance:
            return Response({"msg": "Объект не найден"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ServiceAccountSerializer(instance, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = ServiceAccountSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)


class ServiceAccountActivateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        account_id = self.kwargs.get('account_id')

        if user.is_staff:
            token = token_hex(16)
            token_instance = OneTimeToken.objects.filter(account_id=account_id).first()
            if token_instance:
                token_instance.delete()
            OneTimeToken.objects.create(account_id=account_id, token=token)
            return Response({"token": token}, status=status.HTTP_201_CREATED)
        else:
            return Response({"msg": "Недостаточно прав"}, status=status.HTTP_403_FORBIDDEN)
