from datetime import timezone

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# Create your models here.
class Location(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
    )

    def __str__(self):
        return self.name

    class Meta:
        unique_together = [("latitude", "longitude")]


class Scenario(models.Model):
    name = models.CharField(max_length=100, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="scenarios")
    # Only few Steps are marked as root
    # TODO: rethink creation, because this should be non-nullable
    root_step = models.ForeignKey(
        "Step", on_delete=models.CASCADE, related_name="as_root_for_scenario", null=True
    )

    # TODO: In Future MULTIPLAYER
    # limit_players = models.PositiveIntegerField(
    #     validators=[MinValueValidator(1), MaxValueValidator(1)]
    # )

    def save(self, *args, **kwargs):
        # if not self.root_step:
        #     raise ValidationError("Scenario requires a root step.")
        # if self.root_step.scenario != self:
        #     raise ValidationError("Root step must belong to this scenario.")

        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Step(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    scenario = models.ForeignKey(
        Scenario, on_delete=models.CASCADE, related_name="steps"
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Location where this decision is made",
    )

    def clean(self):
        """Enforces maximum 4 choices per step"""
        if self.choices.count() > 4:
            raise ValidationError("A step cannot have more than 4 choices.")

    def is_last_step(self) -> bool:
        return self.choices.count() == 0

    def __str__(self):
        return f"{self.scenario.name} - {self.title}"


class Choice(models.Model):
    # What step the choice belongs to
    step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=50)
    next = models.ForeignKey(
        Step, on_delete=models.CASCADE, related_name="previous_choices"
    )

    def clean(self):
        """Ensures choices point to steps in the same scenario"""
        if self.next.scenario != self.step.scenario:
            raise ValidationError("Next step must belong to the same scenario.")
        if self.step.choices.exclude(id=self.id).count() >= 4:
            raise ValidationError("A step cannot have more than 4 choices.")

    # TODO: reconsider following properties
    # order = models.PositiveSmallIntegerField(default=0, help_text="Display order")
    # class Meta:
    #     ordering = ["order"]
    #     contraints = [
    #         models.UniqueConstraint(
    #             fields=["step", "order"], name="unique_order_per_step"
    #         )
    #     ]


class Game(models.Model):
    # TODO: Multiplayer with M2M field for Game
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="games")
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    current_step = models.ForeignKey(
        Step, on_delete=models.SET_NULL, null=True, related_name="active_games"
    )
    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(null=True)

    @property
    def status(self) -> str:
        if self.end is None:
            return "running"
        return "ended"

    @property
    def total_playtime(self):
        return sum((s.duration for s in self.sessions.all()), timezone.timedelta())

    def __str__(self):
        return f"{self.scenario.name} played by {self.user.username}"


class Session(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="sessions")
    start = models.DateTimeField(auto_now=True)
    end = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    @property
    def duration(self):
        return (self.end or timezone.now()) - self.start

    def __str__(self):
        return f"session for {self.game.id} ({self.is_active})"


class History(models.Model):
    session = models.ForeignKey(
        "Session", on_delete=models.CASCADE, related_name="decisions"
    )
    choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True)
    step = models.ForeignKey(
        Step,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Snapshot of the step at decision time.",
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History for {self.session}"

    class Meta:
        ordering = ["-timestamp"]
