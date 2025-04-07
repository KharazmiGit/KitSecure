from rest_framework import serializers
from . import models




# create and retrive data ==> usr's actions 
class UserActionSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.UserAction
        fields = ['id', 'user', 'json_data', 'created_at']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        return models.UserAction.objects.create(**validated_data)
    
    
    