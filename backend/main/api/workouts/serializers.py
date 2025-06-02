from rest_framework import serializers
from django.contrib.auth.models import User

from main.models.workout import Workout
from main.api.users.serializers import UserPublicSerializer

class WorkoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workout
        fields = ['id', 'workoutName', 'workoutCategory', 'level', 'gender', 'likes_count', 'creationDate', 'bodyPart']


class WorkoutDetailSerializer(serializers.ModelSerializer):
    creator = UserPublicSerializer(read_only=True)
    class Meta:
        model = Workout
        fields = '__all__'
