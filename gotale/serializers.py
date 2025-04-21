from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from core.serializers import BaseModelSerializer, UserSerializer
from gotale.models import Choice, Game, Location, Scenario, Step

User = get_user_model()


class LocationSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Location
        fields = BaseModelSerializer.Meta.fields + (
            "title",
            "description",
            "longitude",
            "latitude",
        )


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "text"]


class StepSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Step

        fields = ["id", "title", "description", "location", "choices"]


class ScenarioSerializer(BaseModelSerializer):
    author = UserSerializer(read_only=True)
    root_step = StepSerializer()

    class Meta(BaseModelSerializer.Meta):
        model = Scenario
        fields = BaseModelSerializer.Meta.fields + (
            "author",
            "root_step",
            "description",
            "title",
        )


class ChoiceCreateSerializer(serializers.ModelSerializer):
    next = serializers.IntegerField(required=True)

    class Meta:
        model = Choice
        fields = ["text", "next"]


class StepCreateSerializer(serializers.ModelSerializer):
    choices = ChoiceCreateSerializer(many=True)
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Step
        fields = ["id", "title", "description", "location", "choices"]


class ScenarioCreateSerializer(BaseModelSerializer):
    steps = StepCreateSerializer(many=True)

    class Meta(BaseModelSerializer.Meta):
        model = Scenario
        fields = BaseModelSerializer.Meta.fields + (
            "author",
            "steps",
            "description",
            "title",
        )
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + ("author",)

    def validate_steps(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("A scenario must have at least one step.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        steps_data = validated_data.pop("steps")
        scenario = Scenario.objects.create(**validated_data)

        front_id_to_step = {}  # Map front-end IDs to back-end IDs
        steps_to_create = []
        choices_to_create = []
        for i, step_data in enumerate(steps_data):
            step_id = step_data.pop("id")  # Prevent frontend from sending id
            choices_data = step_data.pop("choices")

            step = Step(scenario=scenario, **step_data)

            steps_to_create.append((step, choices_data))
            front_id_to_step[step_id] = step

        created_steps = Step.objects.bulk_create([s[0] for s in steps_to_create])

        if created_steps:
            scenario.root_step = created_steps[0]
            scenario.save(update_fields=["root_step"])  # Only save 'root_step'

        for step, choices_data in zip(created_steps, [s[1] for s in steps_to_create]):
            for choice_data in choices_data:
                next_id = choice_data.pop("next")
                choice_data["next"] = front_id_to_step.get(next_id)
                choices_to_create.append(Choice(step=step, **choice_data))

        Choice.objects.bulk_create(choices_to_create)

        return scenario


class GameSerializer(BaseModelSerializer):
    current_step = StepSerializer(read_only=True)

    class Meta(BaseModelSerializer.Meta):
        model = Game
        fields = BaseModelSerializer.Meta.fields + ("current_step",)


# class GameWriteSerializer(serializers.ModelSerializer):
#     current_step = StepSerializer(write)
#     class Meat:
#         model = Game
#         fields = "-all"


class MakeChoiceSerializer(serializers.Serializer):
    choice_id = serializers.IntegerField(required=True)
