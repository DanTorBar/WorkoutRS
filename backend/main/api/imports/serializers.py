from rest_framework import serializers

class ImportHealthDataSerializer(serializers.Serializer):
    file = serializers.FileField(help_text="ZIP file with exported data")
    source = serializers.CharField(
        help_text="Data source key, e.g. 'garmin', 'fitbit', etc."
    )