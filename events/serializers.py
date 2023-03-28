from rest_framework import serializers
from main.models import *


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields='__all__'


class EventsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Events
        fields='__all__'



class PackagesSerializer(serializers.ModelSerializer):
    class Meta:
        model=Packages
        fields='__all__'



class CartedEventSerializer(serializers.ModelSerializer):
    class Meta:
        model=CartedEvent
        fields='__all__'



class PayedEventSerializer(serializers.ModelSerializer):
    class Meta:
        model=PayedEvents
        fields='__all__'