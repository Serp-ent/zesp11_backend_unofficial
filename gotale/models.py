from datetime import datetime
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_extensions.db.models import (
    TitleDescriptionModel,
)

from core.models import BaseModel, BaseTrackedModel, User
from gotale.choices import GameStatus


class Location(TitleDescriptionModel, BaseTrackedModel):
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(Decimal("-90.0")),
            MaxValueValidator(Decimal("90.0")),
        ],
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(Decimal("-180.0")),
            MaxValueValidator(Decimal("180.0")),
        ],
    )

    def __str__(self):
        return self.title

    class Meta:
        unique_together = [("latitude", "longitude")]


class Scenario(TitleDescriptionModel, BaseTrackedModel):
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
        return self.title


class Step(TitleDescriptionModel, BaseModel):
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
        return f"{self.scenario.title} - {self.title}"


class Choice(BaseModel):
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

    def __str__(self):
        return self.text


class Game(BaseModel):
    # TODO: Multiplayer with M2M field for Game
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="games")
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    current_step = models.ForeignKey(
        Step, on_delete=models.SET_NULL, null=True, related_name="active_games"
    )
    end = models.DateTimeField(null=True)

    @property
    def status(self) -> GameStatus:
        if self.current_step.choices.count() == 0:
            return GameStatus.ENDED
        return GameStatus.RUNNING

    def __str__(self):
        return f"{self.scenario.title} played by {self.user.username}"

    def make_decision(self, choice):
        if self.status == GameStatus.ENDED:
            raise ValidationError("Game is not active.")

        if choice.step != self.current_step:
            raise ValidationError("Invalid choice for current step.")

        # TODO: record decision using History custom manager

        self.current_step = choice.next
        if self.current_step.is_last_step():
            self.end = datetime.now()
        self.save()


class History(BaseTrackedModel):
    game = models.ForeignKey("Game", on_delete=models.CASCADE, related_name="decisions")
    choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True)
    step = models.ForeignKey(
        Step,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Snapshot of the step at decision time.",
    )

    def __str__(self):
        return f"History for {self.game}"

    class Meta:
        ordering = ["-created_at"]
