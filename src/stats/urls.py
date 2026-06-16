from django.urls import path

from stats.views import BestPostsView, SnapshotView

urlpatterns = [
    path('<int:group_id>/best/', best_posts_view),
    path('<int:group_id>/', snapshot_view)
]
