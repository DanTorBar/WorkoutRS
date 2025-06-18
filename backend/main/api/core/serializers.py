from rest_framework import serializers
from main.models.workout import Workout
from main.models.exercise import Exercise
from main.api.workouts.serializers import WorkoutDetailSerializer
from main.api.exercises.serializers import ExerciseSerializer

class RecommendedWorkoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workout
        fields = '__all__'

class RecommendedExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'
