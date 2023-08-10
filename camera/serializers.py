from rest_framework import serializers

from camera.models import IPAddressModel


class IPAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPAddressModel
        fields = ["name", "address"]
