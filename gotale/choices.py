from django.db import models
from django.utils.translation import gettext_lazy as _


class GameStatus(models.TextChoices):
    RUNNING = "RUNNING", _("running")
    ENDED = "ENDED", _("ended")
