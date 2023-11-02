from rest_framework import serializers
from main_app.models import LifeSituation
from main_app.serializers.service_serializers import ServiceListSerializer
from main_app.utils import generate_life_situation_identifier

class LifeSituationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LifeSituation
        fields = '__all__'


class LifeSituationListSerializer(LifeSituationSerializer):
    services = ServiceListSerializer(many=True, read_only=True)
    name = serializers.CharField(source='get_name_display', read_only=True, label="Жизненная ситуация")
    class Meta:
        model = LifeSituation
        fields = ['id', 'name', 'identifier', 'services']


class LifeSituationRetrieveSerializer(LifeSituationSerializer):
    class Meta:
        model = LifeSituation
        fields = ['id', 'identifier', 'name']


class LifeSituationCreateSerializer(LifeSituationSerializer):
    class Meta:
        model = LifeSituation
        fields = ['name', 'identifier']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        identifier = generate_life_situation_identifier(user=user)
        validated_data['identifier'] = identifier
        return LifeSituation.objects.create(**validated_data)


class LifeSituationUpdateSerializer(LifeSituationSerializer):
    class Meta:
        model = LifeSituation
        fields = ['id', 'name']
