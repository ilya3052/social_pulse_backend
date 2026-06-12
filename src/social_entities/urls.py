from django.urls import path

from social_entities.views import PredictiveModelsView, platform_view, groups_create_view, groups_list_view, \
    groups_compare_view, group_check_access_view, groups_get_post_info_view, groups_delete_update_view, \
    groups_retrieve_by_slug_view

urlpatterns = [
    path('platforms/', platform_view, name='platforms'),

    path('groups/', groups_create_view, name='groups-get-create'),
    path('groups/all/', groups_list_view, name='groups-get-create'),
    path('groups/compare/', groups_compare_view, name='compare-groups'),
    path('groups/check-access/', group_check_access_view, name='check-group-access'),
    path('groups/<int:pk>/get-post/', groups_get_post_info_view, name='groups-get-post'),
    path('groups/<int:pk>/', groups_delete_update_view, name='groups-delete-update'),
    path('groups/<str:slug>/', groups_retrieve_by_slug_view, name='groups-retrieve'),

    path('predictive-models/', PredictiveModelsView.as_view(), name='predictive-models'),
]
