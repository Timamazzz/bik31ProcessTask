from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LifeSituationViewSet, ServiceViewSet, ProcessViewSet, UserViewSet

router = DefaultRouter()
router.register(r'lifesituations', LifeSituationViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'processes', ProcessViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
