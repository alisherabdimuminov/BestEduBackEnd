from rest_framework import serializers

from .models import User

class UserGETSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "middle_name", "bio", "image", "is_student"]

class UserSignUpSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(raw_password=password)
        user.save()
        return user
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "middle_name", "bio", "image", "is_student", "password"]


class UserPOSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "middle_name", "bio", "image", "is_student"]

class GeneratePayLinkSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    amount = serializers.IntegerField()
