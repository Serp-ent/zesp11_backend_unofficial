from django.contrib.auth import get_user_model
from rest_framework import serializers

from gotale.models import Choice, Game, Location, Scenario, Step

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "id",
            "last_name",
            "username",
            "date_joined",
        )


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "password",
            "last_name",
            "username",
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "password",
            "last_name",
            "username",
            "date_joined",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


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


class ChoiceSerializers(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "text"]


class StepSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializers(many=True, read_only=True)

    class Meta:
        model = Step
        fields = ["id", "title", "description", "location", "choices"]


class ScenarioSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    root_step = StepSerializer()

    class Meta:
        model = Scenario
        fields = "__all__"


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
