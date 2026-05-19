from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from unidecode import unidecode

from social_pulse import settings


def default_expires_at():
    return timezone.now() + settings.SHORT_TOKEN_LIFETIME


class Group(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["external_id", "platform"],
                name='uq_group_platform_external'
            )
        ]

    name = models.CharField(max_length=128)
    link = models.CharField(max_length=256)
    external_id = models.BigIntegerField(db_index=True)
    added_at = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    platform = models.ForeignKey('Platform', on_delete=models.CASCADE)
    users = models.ManyToManyField('users.CustomUser')
    service_account = models.ForeignKey('service_accounts.ServiceAccount', on_delete=models.SET_NULL, null=True,
                                        related_name='groups')

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(unidecode(self.name))
            slug = base_slug
            counter = 1
            while self.__class__.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        return super().save(*args, **kwargs)


class Platform(models.Model):
    alias = models.CharField(max_length=16, db_index=True)
    name = models.CharField(max_length=128)

class PredictiveModels(models.Model):
    RIDGE = 'Ridge Regression'
    LASSO = 'Lasso Regression'
    ELASTIC_NET = 'Elastic Net Regression'
    SVR = 'Support Vector Regression'
    GRADIENT_BOOSTING = 'Gradient Boosting Regressor'
    model_type = (
        (RIDGE, 'Ridge Regression'),
        (LASSO, 'Lasso Regression'),
        (ELASTIC_NET, 'Elastic Net Regression'),
        (SVR, 'Support Vector Regression'),
        (GRADIENT_BOOSTING, 'Gradient Boosting Regressor'),
    )

    predictable_variable = models.CharField(max_length=16)
    params = models.JSONField()
    model = models.CharField(max_length=128, choices=model_type)

    r2 = models.FloatField()
    mae = models.FloatField()
    rmse = models.FloatField()
    residual_std = models.FloatField()


    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='predictive_models')
