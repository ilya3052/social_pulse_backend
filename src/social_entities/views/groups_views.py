import json

from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.config import SPECIAL_VK_ACC_SERVICE_KEY
from common.utils.producer import publish_task
from service_accounts.services import get_service_account_data
from social_entities.models import Group
from social_entities.permissions import IsOwner
from social_entities.serializers import GroupSerializer
from social_entities.services import check_access_function, get_group_info, delete_group, compare_groups, get_post_info
from social_entities.utils import Platforms
from stats.models import AbsoluteStats


class GroupMixin:
    serializer_class = GroupSerializer
    pagination_class = None
    operation_mode = None

    def get_serializer_context(self):
        context = super().get_serializer_context()
        exclude_fields_str = self.request.GET.get('exclude_fields')
        exclude_fields = exclude_fields_str.split(',') if exclude_fields_str else []
        context['exclude_fields'] = exclude_fields
        return context

    def get_queryset(self):
        queryset = self.get_base_queryset()
        if self.operation_mode == "rebalancing":
            return queryset
        queryset = queryset.filter(**self.get_filter_kwargs())
        return queryset

    def get_base_queryset(self):
        return Group.objects.prefetch_related('users', 'abs_stats')

    def get_filter_kwargs(self):
        filters = {}
        if q := self.request.GET.get('q'):
            filters['name__icontains'] = q
        return filters


class GroupsCreateView(GroupMixin, generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        external_id = request.data.get('external_id')
        platform = request.data.get('platform_id')
        user = self.request.user
        if not external_id or not platform:
            return Response(
                {"detail": "external_id и platform_id обязательны"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            group = Group.objects.get(external_id=external_id, platform=platform)
            # publish_task(json.dumps({"group_id": group.id, 'tg_id': user.tg_id}))
            group.users.add(user)
            return Response(status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            data = request.data.copy()
            data['users_ids'] = [user.id]
            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            group = serializer.save()

            publish_task(json.dumps({"group_id": group.id, 'tg_id': user.tg_id}))

            AbsoluteStats.objects.create(group=group)
            return Response(status=status.HTTP_201_CREATED)


class GroupsDeleteUpdateView(GroupMixin, generics.DestroyAPIView, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated & IsOwner]
    operation_mode = "rebalancing"

    def destroy(self, request, *args, **kwargs):
        group = self.get_object()
        user = request.user
        status_code = delete_group(group, user)
        return Response(status=status_code)


class GroupsListView(GroupMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated & IsOwner]

    def get_queryset(self):
        return super().get_queryset().order_by('abs_stats__participants_count')


class GroupsRetrieveByIDView(GroupMixin, generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated & IsOwner]
    lookup_field = 'pk'


class GroupsRetrieveBySlugView(GroupMixin, generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated & IsOwner]
    lookup_field = 'slug'

    def get_queryset(self):
        return (super()
                .get_base_queryset()
                .prefetch_related('service_account__data')
                .select_related('platform')
                .prefetch_related('users')
                .filter(users__in=[self.request.user]))

    def retrieve(self, request, *args, **kwargs):
        group = self.get_object()

        platform = Platforms(group.platform.alias)
        data = get_service_account_data(group.service_account, platform)

        options = {}
        if "service_key" in data:
            options['service_key'] = data.get('service_key')
        elif "session_path" in data:
            options['session_path'] = data.get('session_path')

        result = get_group_info(group.external_id, Platforms(group.platform.alias), **options)
        if "error_code" in result:
            return Response(status=result.get('error_code'))

        description = result.get('description')
        photo_url = result.get('photo_url')

        serializer = self.get_serializer(group)

        return Response({**serializer.data, "description": description, "photo_url": photo_url},
                        status=status.HTTP_200_OK)


class CheckGroupAccessView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        internal_data: dict = request.data

        platform_alias = internal_data.get('platform')
        platform = Platforms(platform_alias)

        result, status_code = check_access_function.get(platform)(internal_data)
        return Response(result, status_code)


class CompareGroupsView(APIView):
    permission_classes = [IsAuthenticated & IsOwner]

    context = {
        'exclude_fields': ['last_updated_at']
    }

    def get(self, request, *args, **kwargs):
        compare_result, status_code = compare_groups(request.GET.dict(), context=self.context)
        return Response(compare_result, status=status_code)


class GroupsGetPostInfoView(APIView):
    permission_classes = [IsAuthenticated & IsOwner]

    def get(self, request, *args, **kwargs):
        group = Group.objects.select_related('platform').prefetch_related('service_account__data').get(
            pk=self.kwargs['pk'])
        self.check_object_permissions(request, group)

        platform = Platforms(group.platform.alias)

        options = {}
        if platform == Platforms.VK:
            options['service_key'] = SPECIAL_VK_ACC_SERVICE_KEY
        else:
            options['session_path'] = group.service_account.data.session_path

        post_data, status_code = get_post_info(group, platform, request.GET.dict().get('post_id'), **options)

        return Response(post_data, status=status_code)


groups_create_view = GroupsCreateView.as_view()
groups_delete_update_view = GroupsDeleteUpdateView.as_view()
groups_list_view = GroupsListView.as_view()
groups_retrieve_by_id_view = GroupsRetrieveByIDView.as_view()
groups_retrieve_by_slug_view = GroupsRetrieveBySlugView.as_view()
group_check_access_view = CheckGroupAccessView.as_view()
groups_compare_view = CompareGroupsView.as_view()
groups_get_post_info_view = GroupsGetPostInfoView.as_view()
