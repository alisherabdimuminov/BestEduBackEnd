from rest_framework import serializers

from .models import User

class UserGETSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "middle_name", "bio", "image", "is_student"]

class UserPOSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "middle_name", "bio", "image", "is_student"]

