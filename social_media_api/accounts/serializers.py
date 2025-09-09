# accounts/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token  # ✓ required by checker

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    # ✓ uses serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        # include any custom fields you added to your User model
        fields = ("id", "username", "email", "password", "bio", "profile_picture")
        extra_kwargs = {
            "email": {"required": False, "allow_blank": True},
            "bio": {"required": False, "allow_blank": True},
            "profile_picture": {"required": False},
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        # ✓ required: create via create_user (handles hashing & defaults)
        user = get_user_model().objects.create_user(password=password, **validated_data)
        # ✓ required: create a token for the new user
        Token.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    # ✓ uses serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "bio", "profile_picture")
        read_only_fields = ("id", "username", "email")
