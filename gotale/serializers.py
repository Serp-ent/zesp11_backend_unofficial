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

        # Create a mapping of step IDs to their choices
        step_choices, errors = self.get_step_mapping(value)
        if (
            errors
        ):  # Check for duplicate step IDs and informa the user only about that in the first place
            raise serializers.ValidationError(errors)

        referenced_ids = set()
        for step_id, choices in step_choices.items():
            if len(choices) > 4:
                errors.append(
                    f"Step {step_id} has more than 4 choices. A step cannot have more than 4 choices."
                )
            for choice in choices:
                # Check for choice references to steps that don't exist
                if choice["next"] not in step_choices:
                    errors.append(
                        f"Step {step_id} has a choice pointing to non-existent step {choice}."
                    )
                else:
                    referenced_ids.add(choice["next"])

        root_ids = step_choices.keys() - referenced_ids
        if len(root_ids) == 0:
            errors.append(
                "No root step found. At least one step must not be a target of any choice."
            )
        elif len(root_ids) > 1:
            errors.append(
                f"Multiple root steps found: {list(root_ids)}. There must be exactly one root step."
            )

        if errors:
            raise serializers.ValidationError(errors)

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

    def get_step_mapping(self, steps):
        # Oneliner unsafe (allows repeating id)
        # step_choices = {step["id"]: step["choices"] for step in value}
        errors = []
        step_choices = {}
        for step in steps:
            step_id = step["id"]
            choices = step["choices"]
            if step_id in step_choices:
                errors.append(f"Step with id {step_id} is duplicated.")
            step_choices[step_id] = choices

        return step_choices, errors


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
