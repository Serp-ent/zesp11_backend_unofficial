import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django_extensions.db.models import TimeStampedModel

# Create your models here.


class BaseModel(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        unique=True,
    )
    # TODO: created by
    # TODO: updated by

    class Meta:
        abstract = True
        ordering = ["-created"]


class User(BaseModel, AbstractUser):
    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
    )
    password = models.CharField(
        max_length=255,
        blank=False,
        null=False,
    )

    def __str__(self):
        return self.username
