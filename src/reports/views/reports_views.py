import os
from datetime import timedelta

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from reports.models import Report
from reports.serializers import ReportSerializer
from reports.utils import generate_admin_report_excel, generate_admin_report_pdf, generate_group_report_excel, \
    generate_group_report_pdf, sanitize, generate_comparative_report_excel, convert_xlsx_to_pdf
from service_accounts.services import get_service_accounts_aggregated_info, get_service_accounts_loading, \
    get_service_account_data
from social_entities.models import Group
from social_entities.permissions import IsOwner
from social_entities.services import get_group_aggregated_info, get_info_for_group_report, compare_groups
from social_entities.utils import Platforms


def _apply_period_filter(period):
    now = timezone.now()
    periods = {
        'day': now - timedelta(days=1),
        'week': now - timedelta(weeks=1),
        'month': now - timedelta(days=30),
        'year': now - timedelta(days=365),
    }

    if date_from := periods.get(period):
        return {'date__gte': date_from}
    return {}


class UserReportsView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & IsOwner]
    serializer_class = ReportSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        exclude_fields_str = self.request.GET.get('exclude_fields')
        exclude_fields = exclude_fields_str.split(',') if exclude_fields_str else []
        context['exclude_fields'] = exclude_fields
        return context

    def get_queryset(self):
        filters = self.request.GET

        field_mapping = {
            'platform': lambda v: {'group__platform__alias': v.upper()},
            'report_format': lambda v: {'format': v.upper()},
            'report_type': lambda v: {'type': v},
            'search': lambda v: {'filename__icontains': v},
        }

        filters_list = {}
        for param, mapper in field_mapping.items():
            if value := filters.get(param):
                filters_list.update(mapper(value))

        if period := filters.get('period'):
            period_filters = _apply_period_filter(period)
            filters_list.update(period_filters)

        queryset = Report.objects.all().select_related('group__platform').order_by('id')
        if filters_list:
            queryset = queryset.filter(**filters_list)
        return queryset


class AdminReportPDFView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        data = request.data
        report_format = data.get('type', 'XLSX')

        report_data = {
            "service_account_loading": get_service_accounts_loading(),
            "service_account_aggregated_info": get_service_accounts_aggregated_info(),
            "group_aggregated_info": get_group_aggregated_info()
        }
        filepath, relative_path = generate_admin_report_excel(report_data)

        if report_format == 'PDF':
            filepath, relative_path = generate_admin_report_pdf(filepath)

        data['filename'] = os.path.splitext(os.path.basename(filepath))[0]
        data['path'] = filepath
        data['user'] = self.request.user.id
        data['format'] = report_format
        data['type'] = 'admin'
        serializer = ReportSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(relative_path, status=status.HTTP_200_OK)


class GroupReportsView(APIView):
    permission_classes = [IsAuthenticated & IsOwner]

    def get(self, request, *args, **kwargs):
        report_type = request.GET.dict().get('type', 'XLSX')
        group_id = kwargs.get('pk')
        group = (Group.objects
                 .prefetch_related('service_account__data')
                 .select_related('platform')
                 .prefetch_related('best_posts')
                 .prefetch_related('abs_stats')
                 .get(pk=group_id))

        self.check_object_permissions(self.request, group)
        platform = Platforms(group.platform.alias)

        service_account_data = get_service_account_data(group.service_account, platform)

        options = {}
        if "service_key" in service_account_data:
            options['service_key'] = service_account_data.get('service_key')
        elif "session_path" in service_account_data:
            options['session_path'] = service_account_data.get('session_path')

        report_data = get_info_for_group_report(group, platform, **options)
        del report_data['main_info']['photo_url']
        report_data['main_info']['group_name'] = group.name
        report_data['main_info']['platform'] = platform.value

        filepath, relative_path = generate_group_report_excel(report_data)

        if report_type == 'PDF':
            filepath, relative_path = generate_group_report_pdf(filepath, sanitize(group.name))

        data = {
            "filename": os.path.splitext(os.path.basename(filepath))[0],
            "path": filepath,
            "user": self.request.user.id,
            "format": report_type,
            "type": "by_group",
            "group": group.pk
        }

        serializer = ReportSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(relative_path, status=status.HTTP_200_OK)


class CompareGroupReportView(APIView):
    permission_classes = [IsAuthenticated]

    context = {
        'exclude_fields': ['last_updated_at']
    }

    def get(self, request, *args, **kwargs):
        report_type = request.GET.dict().get('type', 'XLSX')
        compare_result, _ = compare_groups(request.GET.dict(), context=self.context)
        filepath, relative_path = generate_comparative_report_excel(compare_result)

        if report_type == 'PDF':
            filepath, relative_path = convert_xlsx_to_pdf(filepath, 'comparative')

        data = {
            "filename": os.path.splitext(os.path.basename(filepath))[0],
            "path": filepath,
            "user": self.request.user.id,
            "format": report_type,
            "type": "comparative",
        }

        serializer = ReportSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(relative_path, status=status.HTTP_200_OK)


user_reports_view = UserReportsView.as_view({'get': 'list'})
admin_report_pdf_view = AdminReportPDFView.as_view()
group_reports_view = GroupReportsView.as_view()
compare_groups_view = CompareGroupReportView.as_view()
