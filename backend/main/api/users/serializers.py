from rest_framework import serializers
from datetime import date
from main.constants import ACTIVITY_LEVEL_CHOICES
from django.contrib.auth import get_user_model
from django.utils import timezone
from main.models.users import HealthProfile, HealthDataConsent

class HealthProfileSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()
    bmi = serializers.SerializerMethodField()
    goals = serializers.ListField(child=serializers.CharField(), required=False)
    conditions = serializers.ListField(child=serializers.CharField(), required=False)
    equipment = serializers.ListField(child=serializers.CharField(), required=False)
    environment = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = HealthProfile
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender', 'height_cm',
            'weight_kg', 'age', 'bmi', 'goals', 'conditions', 'environment', 'equipment',
            'imported_neat_min', 'imported_cardio_mod_min',
            'imported_cardio_vig_min', 'neat_level', 'cardio_mod_level',
            'cardio_vig_level', 'strength_level', 'created_at', 'updated_at'
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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['goals'] = instance.get_goals_list()
        data['conditions'] = instance.get_conditions_list()
        data['equipment'] = instance.get_equipment_list()
        data['environment'] = instance.get_environment_list()
        return data

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        # Convert lists to comma-separated strings
        ret['goals'] = ','.join(data.get('goals', []))
        ret['conditions'] = ','.join(data.get('conditions', []))
        ret['equipment'] = ','.join(data.get('equipment', []))
        ret['environment'] = ','.join(data.get('environment', []))
        return ret

User = get_user_model()

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
        profile_data['user'] = user
        profile = HealthProfile.objects.create(**profile_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    health_profile = HealthProfileSerializer(source='healthprofile', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'first_name', 'last_name',
            'health_profile', 'is_staff'
        ]
        read_only_fields = ['id', 'username', 'email', 'is_staff']

class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class UserFullProfileSerializer(serializers.ModelSerializer):
    health_profile = HealthProfileSerializer(source="healthprofile", read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'health_profile', 'is_staff'
        ]
        read_only_fields = ['id', 'username', 'email', 'is_staff']

