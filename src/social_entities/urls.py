from django.urls import path

from social_entities.views import PlatformsView, GroupsViewByID, CheckGroupAccessView, GroupsViewBySlug, \
    CompareGroupsView, PredictiveModelsView, GroupsGetPostInfoView

urlpatterns = [
    path('platforms/', PlatformsView.as_view({"get": "list", "post": "create"}), name='platforms'),

    path('groups/', GroupsViewByID.as_view({"get": "list", "post": "create"}), name='groups-get-create'),
    path('groups/compare/', CompareGroupsView.as_view(), name='compare-groups'),
    path('groups/check-access/', CheckGroupAccessView.as_view(), name='check-group-access'),
    path('groups/<int:pk>/get-post/', GroupsGetPostInfoView.as_view(), name='groups-get-post'),
    path('groups/<int:pk>/', GroupsViewByID.as_view(
        {"delete": "destroy", "patch": "partial_update"}
    ), name='groups-delete-update'),
    path('groups/<str:slug>/', GroupsViewBySlug.as_view({"get": "retrieve"}), name='groups-retrieve'),

    path('predictive-models/<int:group_id>/', PredictiveModelsView.as_view(), name='predictive-models'),
]