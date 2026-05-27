from rest_framework import serializers

from social_entities.models import PredictiveModels


class PredictiveModelSerializer(serializers.ModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        exclude_fields = self.context.get('exclude_fields', [])

        for field in exclude_fields:
            fields.pop(field, None)
        return fields

    class Meta:
        model = PredictiveModels
        fields = '__all__'
