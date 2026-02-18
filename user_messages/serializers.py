from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'name', 'email', 'content', 'is_read']
        read_only_fields = ['id', 'is_read']  # don't allow clients to mark as read on creation
