from rest_framework import serializers

from main.models.workout import Workout

class WorkoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workout
        fields = ['id', 'workoutName', 'category', 'level', 'gender', 'likes_count', 'creationDate']


class WorkoutDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workout
        fields = '__all__'
