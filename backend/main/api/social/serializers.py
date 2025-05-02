from rest_framework import serializers
from main.models.social import Favourite
from main.models.exercise import Exercise
from main.models.workout import Workout

class FavouriteSerializer(serializers.ModelSerializer):
    """
    Serializador para crear y listar favoritos.
    - El campo `user` se asigna en el ViewSet (read_only).
    - Se debe enviar SOLO uno de estos campos: workout o exercise.
    """
    workout = serializers.PrimaryKeyRelatedField(
        queryset=Workout.objects.all(), required=False, allow_null=True
    )
    exercise = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Favourite
        fields = ['id', 'workout', 'exercise', 'date_added']
        read_only_fields = ['id', 'date_added']

    def validate(self, attrs):
        if not attrs.get('workout') and not attrs.get('exercise'):
            raise serializers.ValidationError("Debe indicar un 'workout' o un 'exercise'.")
        if attrs.get('workout') and attrs.get('exercise'):
            raise serializers.ValidationError("Solo debe indicar UNO de: 'workout' o 'exercise'.")
        return attrs

    def create(self, validated_data):
        # Asigna siempre el usuario actual
        user = self.context['request'].user
        fav, created = Favourite.objects.get_or_create(
            user=user,
            workout=validated_data.get('workout'),
            exercise=validated_data.get('exercise')
        )
        return fav