from django.urls import path

from stats.views import best_posts_view, snapshot_view

urlpatterns = [
    path('<int:group_id>/best/', best_posts_view),
    path('<int:group_id>/', snapshot_view)
]
