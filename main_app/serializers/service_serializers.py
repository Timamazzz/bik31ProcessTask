from rest_framework import serializers
from main_app.models import Service
from main_app.serializers.process_serializers import ProcessRetrieveSerializer
from main_app.utils import generate_service_identifier

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class ServiceListSerializer(ServiceSerializer):
    processes = ProcessRetrieveSerializer(many=True, read_only=True)
    service_type = serializers.CharField(source='get_service_type_display', read_only=True, label="Тип")

    class Meta:
        model = Service
        fields = ['id', 'service_type', 'name', 'regulating_act', 'processes', 'identifier']


class ServiceRetrieveSerializer(ServiceSerializer):
    class Meta:
        model = Service
        fields = ['id', 'service_type', 'name', 'regulating_act', 'identifier']


class ServiceCreateSerializer(ServiceSerializer):
    class Meta:
        model = Service
        fields = ['service_type', 'name', 'regulating_act', 'lifesituation', 'identifier']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        identifier = generate_service_identifier(life_situation=validated_data['lifesituation'])
        validated_data['identifier'] = identifier
        return Service.objects.create(**validated_data)


class ServiceUpdateSerializer(ServiceSerializer):
    class Meta:
        model = Service
        fields = ['id', 'service_type', 'name', 'regulating_act']
