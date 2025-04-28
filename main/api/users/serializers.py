from rest_framework import serializers
from datetime import date
from main.constants import ACTIVITY_LEVEL_CHOICES
from django.contrib.auth import get_user_model
from django.utils import timezone

from main.models.users import HealthProfile, HealthDataConsent, Goal, Condition, Equipment

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

class HealthProfileSerializer(serializers.ModelSerializer):
    goals      = serializers.PrimaryKeyRelatedField(many=True, queryset=Goal.objects.all(), required=False)
    conditions = serializers.PrimaryKeyRelatedField(many=True, queryset=Condition.objects.all(), required=False)
    equipment  = serializers.PrimaryKeyRelatedField(many=True, queryset=Equipment.objects.all(), required=False)

    neat_level       = serializers.ChoiceField(choices=ACTIVITY_LEVEL_CHOICES, required=False)
    cardio_mod_level = serializers.ChoiceField(choices=ACTIVITY_LEVEL_CHOICES, required=False)
    cardio_vig_level = serializers.ChoiceField(choices=ACTIVITY_LEVEL_CHOICES, required=False)
    strength_level   = serializers.ChoiceField(choices=ACTIVITY_LEVEL_CHOICES, required=False)

    class Meta:
        model = HealthProfile
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'height_cm', 'weight_kg',
            'goals', 'conditions', 'equipment', 'environment',
            'neat_level', 'cardio_mod_level', 'cardio_vig_level', 'strength_level',
        ]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    health_data_consent = serializers.BooleanField(write_only=True)
    profile = HealthProfileSerializer(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password',
            'health_data_consent',
            'profile',
        ]

    def validate_health_data_consent(self, value):
        if not value:
            raise serializers.ValidationError("Debes aceptar el tratamiento de datos de salud.")
        return value

    def create(self, validated_data):
        # 1) Extraer y validar consentimiento
        consent = validated_data.pop('health_data_consent')

        # 2) Extraer datos de perfil
        profile_data = validated_data.pop('profile')

        # 3) Crear usuario
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        # 4) Crear registro de consentimiento
        HealthDataConsent.objects.create(
            user=user,
            given=consent,
            given_at=timezone.now()
        )

        # 5) Crear HealthProfile
        m2m = {
            'goals':      profile_data.pop('goals', []),
            'conditions': profile_data.pop('conditions', []),
            'equipment':  profile_data.pop('equipment', [])
        }
        profile = HealthProfile.objects.create(user=user, **profile_data)

        # 6) Asignar M2M
        if m2m['goals']:
            profile.goals.set(m2m['goals'])
        if m2m['conditions']:
            profile.conditions.set(m2m['conditions'])
        if m2m['equipment']:
            profile.equipment.set(m2m['equipment'])

        return user

class UserSerializer(serializers.ModelSerializer):
    health_profile = HealthProfileSerializer(source='healthprofile', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'first_name', 'last_name',
            'health_profile',
        ]
        read_only_fields = ['id', 'username', 'email']
