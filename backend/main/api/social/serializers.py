from rest_framework import serializers
from main.models.social import Favourite
from main.models.exercise import Exercise
from main.models.workout import Workout
from main.models.social import Comment

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

        # Verifica si ya existe un favorito para este usuario y este ítem
        existing_fav = Favourite.objects.filter(
            user=user,
            workout=validated_data.get('workout'),
            exercise=validated_data.get('exercise')
        ).first()

        if existing_fav:
            raise serializers.ValidationError("Ya has dado like a este ítem.")

        # Si no existe, crea el favorito
        fav = Favourite.objects.create(
            user=user,
            workout=validated_data.get('workout'),
            exercise=validated_data.get('exercise')
        )
        return fav

    def delete(self, validated_data):
        # Asigna siempre el usuario actual
        user = self.context['request'].user
        try:
            fav = Favourite.objects.get(
                user=user,
                workout=validated_data.get('workout'),
                exercise=validated_data.get('exercise')
            )
            fav.delete()
            return {"detail": "Favorito eliminado correctamente"}
        except Favourite.DoesNotExist:
            raise serializers.ValidationError("El favorito no existe")
        
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    workout = serializers.PrimaryKeyRelatedField(queryset=Workout.objects.all(), required=False, allow_null=True)
    exercise = serializers.PrimaryKeyRelatedField(queryset=Exercise.objects.all(), required=False, allow_null=True)
    reported = serializers.BooleanField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'workout', 'exercise', 'comment', 'date_added', 'reported']
        read_only_fields = ['id', 'user', 'date_added', 'reported']

    def validate(self, attrs):
        if not attrs.get('workout') and not attrs.get('exercise'):
            raise serializers.ValidationError("Debe indicar un 'workout' o un 'exercise'.")
        if attrs.get('workout') and attrs.get('exercise'):
            raise serializers.ValidationError("Solo debe indicar UNO de: 'workout' o 'exercise'.")
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        return Comment.objects.create(user=user, **validated_data)
