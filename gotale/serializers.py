from django.contrib.auth.models import User
from rest_framework import serializers
from gotale.models import Location, Scenario, Step, Game


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "date_joined"]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["name", "longitude", "latitude"]


class ScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = "__all__"
        depth = 1


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ["id", "title", "text", "location", "choices"]
        depth = 1


class GameSerializer(serializers.ModelSerializer):
    current_step = StepSerializer()
    class Meta:
        model = Game
        fields = "__all__"


class MakeChoiceSerializer(serializers.Serializer):
    choice_id = serializers.IntegerField(required=True)
