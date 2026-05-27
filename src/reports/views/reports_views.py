import os

from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from reports.serializers import ReportSerializer
from reports.utils import generate_admin_report_excel, generate_admin_report_pdf
from service_accounts.services import get_service_accounts_aggregated_info, get_service_accounts_loading, \
    get_service_account_data
from social_entities.models import Group
from social_entities.permissions import IsAuthenticatedAndOwner
from social_entities.services import get_group_aggregated_info, get_info_for_group_report, compare_groups
from social_entities.utils import Platforms
from social_pulse.settings import BASE_DIR


class AdminReportPDFView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        data = request.data
        report_type = data.get('type', 'XLSX')

        report_data = {
            "service_account_loading": get_service_accounts_loading(),
            "service_account_aggregated_info": get_service_accounts_aggregated_info(),
            "group_aggregated_info": get_group_aggregated_info()
        }
        filepath, relative_path = generate_admin_report_excel(report_data)

        if report_type == 'PDF':
            filepath, relative_path = generate_admin_report_pdf(filepath)

        data['filename'] = os.path.splitext(os.path.basename(filepath))[0]
        data['path'] = filepath
        data['user'] = self.request.user.id

        serializer = ReportSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        relative_path = os.path.relpath(filepath, BASE_DIR).replace('\\', '/')

        return Response(relative_path, status=status.HTTP_200_OK)


class GroupReportsView(APIView):
    permission_classes = [IsAuthenticatedAndOwner]

    def get(self, request, *args, **kwargs):
        group_id = kwargs.get('pk')
        group = (Group.objects
                 .prefetch_related('service_account__data')
                 .select_related('platform')
                 .prefetch_related('best_posts')
                 .prefetch_related('abs_stats')
                 .get(pk=group_id))
        platform = Platforms(group.platform.alias)

        data = get_service_account_data(group.service_account, platform)

        options = {}
        if "service_key" in data:
            options['service_key'] = data.get('service_key')
        elif "session_path" in data:
            options['session_path'] = data.get('session_path')

        report_info = get_info_for_group_report(group, platform, **options)

        return Response(200)


class CompareGroupReportView(APIView):
    permission_classes = [IsAuthenticatedAndOwner]

    context = {
        'exclude_fields': ['last_updated_at']
    }

    def get(self, request, *args, **kwargs):
        compare_result, status_code = compare_groups(request.GET.dict(), context=self.context)

        return Response(200)
