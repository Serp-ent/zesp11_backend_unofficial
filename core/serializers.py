from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class BaseModelSerializer(serializers.ModelSerializer):
    """Base serializer for all models."""

    class Meta:
        abstract = None
        fields = ("id", "created", "modified")
        read_only_fields = fields
        extra_kwargs = {
            "id": {"read_only": True},
            "created": {"read_only": True},
            "modified": {"read_only": True},
        }


class UserSerializer(BaseModelSerializer):
    created = serializers.DateTimeField(source="date_joined", read_only=True)

    class Meta(BaseModelSerializer.Meta):
        model = User
        fields = BaseModelSerializer.Meta.fields + (
            "email",
            "first_name",
            "last_name",
            "username",
        )


class UserUpdateSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = User
        fields = BaseModelSerializer.Meta.fields + (
            "email",
            "first_name",
            "password",
            "last_name",
            "username",
        )
        extra_kwargs = BaseModelSerializer.Meta.extra_kwargs | {
            "password": {"write_only": True},
        }

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


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
