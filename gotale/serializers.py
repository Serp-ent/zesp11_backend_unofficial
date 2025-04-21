from django.contrib.auth import get_user_model
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


class ChoiceSerializers(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "text"]


class StepSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializers(many=True, read_only=True)

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
