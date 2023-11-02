from django.contrib.auth.base_user import BaseUserManager
from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from main_app.enums import ServiceStatus, ServiceType, LifeSituationName, ProcessGroupEnum


class Organization(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название организации", blank=True, null=True, )
    code = models.CharField(max_length=50, verbose_name="Код организации", unique=True, )

    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"

    def __str__(self):
        return self.code


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('email должен быть указан')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True, null=True,
    )
    patronymic = models.CharField(max_length=30, blank=True, null=True, verbose_name="Отчество")
    email = models.EmailField(unique=True, blank=False, null=False, verbose_name="Email")
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, blank=True, null=True,
                                     verbose_name="Организация")

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class LifeSituation(models.Model):
    name = models.CharField(max_length=100,
                            verbose_name="Жизненная ситуация", blank=True,
                            null=True, )
    identifier = models.CharField(max_length=50, verbose_name="Идентификатор", blank=True, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь", blank=True, null=True, )

    class Meta:
        verbose_name = "Жизненная ситуация"
        verbose_name_plural = "Жизненные ситуации"

    def __str__(self):
        return self.identifier or "None"


class Service(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название услуги", blank=True, null=True, )
    service_type = models.CharField(max_length=10,
                                    choices=[(type.name, type.value) for type in ServiceType],
                                    verbose_name="Тип услуги", blank=True,
                                    null=True, )
    regulating_act = models.CharField(max_length=255, verbose_name="Регулирующий акт", blank=True, null=True, )
    lifesituation = models.ForeignKey(LifeSituation, on_delete=models.CASCADE, verbose_name="Жизненная ситуация",
                                      blank=True, null=True, related_name='services')
    identifier = models.CharField(max_length=50, verbose_name="Идентификатор", blank=True, null=True,
                                  default="017.04.001")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь", blank=True, null=True, )

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self):
        return self.identifier or "None"


class Process(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название процесса", blank=True, null=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Услуга",
                                blank=True, null=True, related_name='processes')
    status = models.CharField(max_length=255, choices=[(type.name, type.value) for type in ServiceStatus],
                              default='in_queue', verbose_name="Статус",
                              blank=True, null=True)
    is_internal_client = models.BooleanField(default=False, verbose_name="Внутренний клиент", blank=True, null=True)
    is_external_client = models.BooleanField(default=False, verbose_name="Внешний клиент", blank=True, null=True)
    responsible_authority = models.CharField(max_length=255, verbose_name="Орган, ответственный за процесс", blank=True,
                                             null=True)
    department = models.CharField(max_length=255, verbose_name="Структурное подразделение органа", blank=True,
                                  null=True)
    is_digital_format = models.BooleanField(default=False, verbose_name="Цифровой формат", blank=True, null=True)
    is_non_digital_format = models.BooleanField(default=False, verbose_name="Не цифровой формат", blank=True, null=True)

    digital_format_link = models.URLField(verbose_name="Ссылка на размещение в цифровом формате", blank=True, null=True)
    identifier = models.CharField(max_length=50, verbose_name="Идентификатор", blank=True, null=True, )

    # Данные
    client_value = models.TextField(verbose_name="Ценность для клиента", blank=True, null=True)
    input_data = models.TextField(verbose_name="Данные на входе", blank=True, null=True)
    output_data = models.TextField(verbose_name="Данные на выходе", blank=True, null=True)
    related_processes = models.TextField(verbose_name="Связанные процессы", blank=True, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь", blank=True, null=True, )
    group = models.CharField(max_length=255, choices=[(group.name, group.value) for group in ProcessGroupEnum],
                             verbose_name="Группа процессов", blank=True, null=True)

    class Meta:
        verbose_name = "Процесс"
        verbose_name_plural = "Процессы"

    def __str__(self):
        return self.identifier or "None"
