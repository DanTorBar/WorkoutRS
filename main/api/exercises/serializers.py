from rest_framework import serializers
from main.models.exercise import Exercise, Muscle

class MuscleSerializer(serializers.ModelSerializer):
    """
    Serializer para representar los músculos.
    """
    class Meta:
        model = Muscle
        fields = ['id', 'name']


class ExerciseSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Exercise.
    - En lectura: muestra los datos completos de los músculos (nested).
    - En escritura: acepta listas de IDs para priMuscles y secMuscles.
    """
    # nested read-only
    priMuscles = MuscleSerializer(many=True, read_only=True)
    secMuscles = MuscleSerializer(many=True, read_only=True)
    # write-only fields para recibir IDs
    priMuscles_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, source='priMuscles', queryset=Muscle.objects.all()
    )
    secMuscles_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, source='secMuscles', queryset=Muscle.objects.all()
    )

    class Meta:
        model = Exercise
        fields = [
            'id',
            'exerciseName',
            'exerciseCategory',
            'priMuscles',      # nested read
            'priMuscles_ids',  # write-only
            'secMuscles',      # nested read
            'secMuscles_ids',  # write-only
            'video',
            'instructions',
            'equipment',
            'likes_count',
        ]
        read_only_fields = ['id', 'likes_count']
