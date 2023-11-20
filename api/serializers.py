from rest_framework import serializers

from api.models import Employee, Camera, Records, Mood


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = '__all__'


class MoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mood
        fields = '__all__'


class RecordsSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    camera = CameraSerializer(read_only=True)
    mood = MoodSerializer(read_only=True)

    class Meta:
        model = Records
        fields = '__all__'
