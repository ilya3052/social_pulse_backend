from django.db import models
from django.utils import timezone


class Report(models.Model):
    report_format = {
        "XLSX": "XLSX",
        "PDF": "PDF"
    }
    report_type = {
        'admin': 'admin',
        'by_group': 'by_group',
        'comparative': 'comparative',
    }
    filename = models.CharField(max_length=256)
    path = models.CharField(max_length=512)
    date = models.DateTimeField(default=timezone.now)
    format = models.CharField(max_length=4, choices=report_format)
    type = models.CharField(max_length=16, choices=report_type)
    group = models.ForeignKey('social_entities.Group', on_delete=models.DO_NOTHING, null=True, blank=True,
                              related_name='report')
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='group_reports')
