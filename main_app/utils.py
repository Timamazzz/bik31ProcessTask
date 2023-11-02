import random
import string

from rest_framework.metadata import SimpleMetadata
from collections import OrderedDict
from django.utils.encoding import force_str
from rest_framework import serializers, viewsets

from main_app.models import LifeSituation, Service, Process


class CustomOptionsMetadata(SimpleMetadata):
    def determine_metadata(self, request, view):
        metadata = super().determine_metadata(request, view)

        serializer_list = getattr(view, 'serializer_list', {})

        if serializer_list:
            actions_metadata = {}
            for key, serializer_class in serializer_list.items():
                serializer_instance = serializer_class()
                fields = self.get_serializer_info(serializer_instance)
                actions_metadata[key] = fields
            metadata['actions'] = actions_metadata

        return metadata

    def get_serializer_info(self, serializer):
        fields = OrderedDict([
            (field_name, self.get_field_info(field))
            for field_name, field in serializer.fields.items()
            if not isinstance(field, serializers.HiddenField)
        ])

        if hasattr(serializer, 'child'):
            fields = self.get_serializer_info(serializer.child)

        return fields

    def get_field_info(self, field):
        field_info = OrderedDict()
        field_info['type'] = self.label_lookup[field]
        field_info['required'] = getattr(field, 'required', False)

        attrs = [
            'read_only', 'label', 'help_text',
            'min_length', 'max_length',
            'min_value', 'max_value'
        ]

        for attr in attrs:
            value = getattr(field, attr, None)
            if value is not None and value != '':
                field_info[attr] = force_str(value, strings_only=True)

        if getattr(field, 'child', None):
            field_info['child'] = self.get_field_info(field.child)
        elif getattr(field, 'fields', None):
            field_info['children'] = self.get_serializer_info(field)

        if (not field_info.get('read_only') and
                not isinstance(field, (serializers.RelatedField, serializers.ManyRelatedField)) and
                hasattr(field, 'choices')):
            field_info['choices'] = [
                {
                    'value': choice_value,
                    'display_name': force_str(choice_name, strings_only=True)
                }
                for choice_value, choice_name in field.choices.items()
            ]

        return field_info


class CustomModelViewSet(viewsets.ModelViewSet):
    serializer_list = {}
    metadata_class = CustomOptionsMetadata

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'create':
            return self.serializer_list.get('create', self.serializer_class)
        elif self.action in ['update', 'partial_update']:
            return self.serializer_list.get('update', self.serializer_class)
        return self.serializer_list.get(self.action, self.serializer_class)


def generate_life_situation_identifier(user=None):
    last_life_situation = LifeSituation.objects.filter(user__organization=user.organization).order_by('-id').count()
    life_situation_count = last_life_situation + 1
    identifier = f"{user.organization.code}.{life_situation_count}"
    return identifier


def generate_service_identifier(life_situation):
    last_service = Service.objects.filter(lifesituation=life_situation).order_by('-id').count()
    service_count = last_service + 1
    identifier = f"{life_situation.identifier}.{service_count}"
    return identifier


def generate_process_identifier(service):
    last_process = Process.objects.filter(service=service).order_by('-id').count()
    process_count = last_process + 1
    identifier = f"{service.identifier}.{process_count}"
    return identifier
