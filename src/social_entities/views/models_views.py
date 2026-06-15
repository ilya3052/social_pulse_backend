import json
import time
from datetime import timedelta, datetime

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from social_entities.models import PredictiveModels, Group
from social_entities.utils import check_post_stats, PostStatus, format_post, Platforms, prepare_post_data
from stats.models import PostMetrics


class PredictiveModelsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            group = Group.objects.select_related('platform').get(id=kwargs['group_id'])
            if group.added_at > timezone.now() - timedelta(days=2):
                return Response({'error_cause': 'post_stats_collected'}, status=status.HTTP_404_NOT_FOUND)
            models = PredictiveModels.objects.filter(group=group)
            if not models:
                return Response({'error_cause': 'model'}, status=status.HTTP_404_NOT_FOUND)
            post_stats = PostMetrics.objects.filter(group=group, timestamp__gt=(timezone.now() - timedelta(days=2)).date())
            if not post_stats:
                return Response({'error_cause': 'post_stats'}, status=status.HTTP_404_NOT_FOUND)

            post_data = []
            for post_stat in post_stats:
                for model in models:
                    post_data.append((check_post_stats(model, post_stat), post_stat.post_id))
            post_data = [data for data in post_data if isinstance(data[0], PostStatus)]

            post_data = [prepare_post_data(data, group) for data in post_data if data]
            return Response(post_data, status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response({'error_cause': 'group'}, status=status.HTTP_404_NOT_FOUND)


