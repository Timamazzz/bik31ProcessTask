from rest_framework import serializers
from main_app.models import Process
from main_app.enums import ServiceStatus
from main_app.utils import generate_process_identifier


class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = '__all__'


class ProcessDataSerializer(ProcessSerializer):
    class Meta:
        model = Process
        fields = ['client_value', 'input_data', 'output_data', 'related_processes', 'group']


class ProcessRetrieveSerializer(ProcessSerializer):
    process_data = ProcessDataSerializer(allow_null=True)

    class Meta:
        model = Process
        fields = ['id', 'name', 'status', 'is_internal_client', 'is_external_client', 'responsible_authority',
                  'department', 'is_digital_format', 'is_non_digital_format', 'digital_format_link', 'identifier',
                  'process_data']

    def to_representation(self, instance):
        data = super(ProcessRetrieveSerializer, self).to_representation(instance)
        process_data = ProcessDataSerializer(instance).data
        data['process_data'] = process_data
        return data


class ProcessCreateSerializer(ProcessSerializer):
    status = serializers.ChoiceField(choices=[(status.name, status.value) for status in ServiceStatus], required=False,
                                     label="Статус")

    class Meta:
        model = Process
        fields = ['name', 'service', 'status', 'is_internal_client', 'is_external_client', 'responsible_authority',
                  'department', 'is_digital_format', 'is_non_digital_format', 'digital_format_link', 'identifier']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        identifier = generate_process_identifier(service=validated_data['service'])
        validated_data['identifier'] = identifier
        return Process.objects.create(**validated_data)


class ProcessUpdateSerializer(ProcessSerializer):
    process_data = ProcessDataSerializer(allow_null=True)
    status = serializers.ChoiceField(choices=[(status.name, status.value) for status in ServiceStatus], required=False,
                                     label="Статус")

    class Meta:
        model = Process
        fields = ['id', 'name', 'status', 'is_internal_client', 'is_external_client', 'responsible_authority',
                  'department',
                  'is_digital_format', 'is_non_digital_format', 'digital_format_link', 'process_data']

    def update(self, instance, validated_data):
        data_fields = validated_data.pop('process_data', {})

        if data_fields:
            for field_name, field_value in data_fields.items():
                setattr(instance, field_name, field_value)

        for field_name, field_value in validated_data.items():
            setattr(instance, field_name, field_value)

        instance.save()
        return super(ProcessUpdateSerializer, self).update(instance, validated_data)
