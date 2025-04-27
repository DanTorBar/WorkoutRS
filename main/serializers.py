from rest_framework import serializers
from datetime import date
from .models import HealthProfile, HealthDataConsent
from django.contrib.auth import get_user_model
from django.utils import timezone

class HealthProfileSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()
    bmi = serializers.SerializerMethodField()

    class Meta:
        model = HealthProfile
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'height_cm', 'weight_kg',
            'age', 'bmi',  # ← añadidos aquí
            'goals', 'medical_conditions',
            'environments', 'available_equipment',
            'imported_neat_min', 'imported_cardio_mod_min',
            'imported_cardio_vig_min', 'imported_strength_min',
            'neat_level', 'cardio_mod_level',
            'cardio_vig_level', 'strength_level',
            'created_at', 'updated_at'
        ]

    def get_age(self, obj):
        if obj.date_of_birth:
            today = date.today()
            return today.year - obj.date_of_birth.year - (
                (today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day)
            )
        return None

    def get_bmi(self, obj):
        if obj.height_cm and obj.weight_kg:
            height_m = obj.height_cm / 100
            return round(float(obj.weight_kg) / (height_m ** 2), 2)
        return None

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    health_data_consent = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'health_data_consent')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_health_data_consent(self, value):
        if not value:
            raise serializers.ValidationError("Debes aceptar el tratamiento de datos de salud.")
        return value

    def create(self, validated_data):
        consent = validated_data.pop('health_data_consent')
        user = super().create(validated_data)
        # Creamos el registro de consentimiento
        HealthDataConsent.objects.create(
            user=user,
            given=consent,
            given_at=timezone.now() if consent else None
        )
        return user