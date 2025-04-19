from django.contrib.auth import get_user_model
from rest_framework import serializers

from gotale.models import Game, Location, Scenario, Step

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = [
            "id",
            "created",
            "modified",
            "title",
            "description",
            "longitude",
            "latitude",
        ]


class ScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = "__all__"
        depth = 1


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ["id", "title", "description", "location", "choices"]
        depth = 1


class GameSerializer(serializers.ModelSerializer):
    current_step = StepSerializer(read_only=True)

    class Meta:
        model = Game
        fields = "__all__"


# class GameWriteSerializer(serializers.ModelSerializer):
#     current_step = StepSerializer(write)
#     class Meat:
#         model = Game
#         fields = "-all"


class MakeChoiceSerializer(serializers.Serializer):
    choice_id = serializers.IntegerField(required=True)
