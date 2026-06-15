import os.path

from rest_framework import serializers

from reports.models import Report
from social_pulse.settings import BASE_DIR


class ReportSerializer(serializers.ModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        exclude_fields = self.context.get('exclude_fields', [])

        for field in exclude_fields:
            fields.pop(field, None)
        return fields

    relative_path = serializers.SerializerMethodField(read_only=True)
    platform = serializers.SerializerMethodField(read_only=True)

    def get_relative_path(self, obj):
        return os.path.relpath(obj.path, BASE_DIR)

    def get_platform(self, obj):
        return obj.group.platform.alias

    class Meta:
        model = Report
        fields = ('id', 'filename', 'user', 'relative_path', 'path', 'date', 'format', 'platform', 'group', 'type')
