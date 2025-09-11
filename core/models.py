import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import (
    CreationDateTimeField,
    ModificationDateTimeField,
)


class BaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        unique=True,
    )

    def __repr__(self):
        return f"<{self._meta.label}(id='{str(self.pk)}')>"

    class Meta:
        abstract = True


class BaseTrackedModel(BaseModel):
    created_at = CreationDateTimeField(_("created"))
    modified_at = ModificationDateTimeField(_("modified"))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_%(class)ss",
        verbose_name=_("created by"),
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name="modified_%(class)ss",
        verbose_name=_("modified by"),
        null=True,
    )

    class Meta:
        abstract = True


class User(BaseModel, AbstractUser):
    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
    )

    def __str__(self):
        return self.username
