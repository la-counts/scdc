from .models import User
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['display_name', 'email', 'title', 'organization',
            'website', 'avatar']
