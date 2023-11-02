from rest_framework import permissions, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import LifeSituation, Service, Process, CustomUser
from .serializers.life_situation_serializers import LifeSituationRetrieveSerializer, LifeSituationCreateSerializer, \
    LifeSituationUpdateSerializer, LifeSituationSerializer, LifeSituationListSerializer
from .serializers.process_serializers import ProcessSerializer, ProcessRetrieveSerializer, ProcessCreateSerializer, \
    ProcessUpdateSerializer
from .serializers.service_serializers import ServiceSerializer, ServiceRetrieveSerializer, ServiceCreateSerializer, \
    ServiceUpdateSerializer
from .serializers.user_serialzers import UserSerializer, UserRetrieveSerializer
from .utils import (generate_life_situation_identifier, generate_service_identifier, generate_process_identifier,
                    CustomModelViewSet)
import random
import string
from post_office import mail
from django.conf import settings
from django.db.models import Q


@api_view(['POST'])
def reset_password(request):
    if request.method == 'POST':
        email = request.data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            new_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
            user.set_password(new_password)
            user.save()

            mail.send(
                [email],
                settings.DEFAULT_FROM_EMAIL,
                subject='Сброс пароля',
                message=f'Ваш новый пароль: {new_password}',
                html_message=f'Ваш новый пароль: {new_password}',
                priority='now')

            return Response({'message': 'Новый пароль отправлен на вашу почту.'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Пользователь с такой почтой не найден.'}, status=status.HTTP_404_NOT_FOUND)


class UserViewSet(CustomModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    serializer_list = {
        'retrieve': UserRetrieveSerializer,
    }
    permission_classes = [permissions.IsAuthenticated]


class LifeSituationViewSet(CustomModelViewSet):
    queryset = LifeSituation.objects.all()
    serializer_class = LifeSituationSerializer
    serializer_list = {
        'list': LifeSituationListSerializer,
        'retrieve': LifeSituationRetrieveSerializer,
        'create': LifeSituationCreateSerializer,
        'update': LifeSituationUpdateSerializer,
    }
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def get_identifier(self, request):
        identifier = generate_life_situation_identifier(user=request.user)
        print('identifier life:', identifier)
        return Response({'identifier': identifier}, status=status.HTTP_200_OK)

    def get_queryset(self):
        user = self.request.user
        organization = user.organization
        queryset = LifeSituation.objects.filter(user__organization=organization)
        return queryset

    def list(self, request, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        search_string = self.request.query_params.get('search', None)
        if search_string:
            queryset = queryset.filter(Q(name__icontains=search_string) | Q(services__name__icontains=search_string))
        queryset = queryset.distinct()
        page = self.paginate_queryset(queryset)
        serializer = LifeSituationListSerializer(page, many=True) if page else LifeSituationListSerializer(queryset,
                                                                                                           many=True)
        return self.get_paginated_response(serializer.data) if page else Response(serializer.data,
                                                                                  status=status.HTTP_200_OK)


class ServiceViewSet(CustomModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    serializer_list = {
        'list': ServiceRetrieveSerializer,
        'retrieve': ServiceRetrieveSerializer,
        'create': ServiceCreateSerializer,
        'update': ServiceUpdateSerializer,
    }
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        organization = user.organization
        queryset = Service.objects.filter(user__organization=organization)
        return queryset

    def list(self, request, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        search_string = self.request.query_params.get('search', None)
        if search_string:
            queryset = queryset.filter(Q(name__icontains=search_string) | Q(services__name__icontains=search_string))
        page = self.paginate_queryset(queryset)
        serializer = ServiceRetrieveSerializer(page, many=True) if page else ServiceRetrieveSerializer(queryset,
                                                                                                       many=True)
        return self.get_paginated_response(serializer.data) if page else Response(serializer.data,
                                                                                  status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_identifier(self, request):
        life_situation_id = request.query_params.get('life_situation_id')
        try:
            life_situation = LifeSituation.objects.get(id=life_situation_id)
        except LifeSituation.DoesNotExist:
            return Response({'error': 'Жизненная ситуация не найдена.'}, status=status.HTTP_404_NOT_FOUND)
        identifier = generate_service_identifier(life_situation)
        print('identifier service:', identifier)
        return Response({'identifier': identifier}, status=status.HTTP_200_OK)


class ProcessViewSet(CustomModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    serializer_list = {
        'list': ProcessRetrieveSerializer,
        'retrieve': ProcessRetrieveSerializer,
        'create': ProcessCreateSerializer,
        'update': ProcessUpdateSerializer,
    }
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def get_identifier(self, request):
        service_id = request.query_params.get('service_id')
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return Response({'error': 'Услуга не найдена.'}, status=status.HTTP_404_NOT_FOUND)
        identifier = generate_process_identifier(service)
        print('identifier process:', identifier)
        return Response({'identifier': identifier}, status=status.HTTP_200_OK)
