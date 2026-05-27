import json

from rest_framework.response import Response
from rest_framework.views import APIView

from social_entities.models import PredictiveModels


class PredictiveModelsView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        model = PredictiveModels.objects.create(model=PredictiveModels.RIDGE,
                                                fields=json.dumps({"views_count": 100, "likes": 250}))

        fields = json.loads(model.params)
        print(fields, type(fields))
        return Response(200)
