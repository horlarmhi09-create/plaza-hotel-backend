from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from user_messages.models import Message
from .serializers import MessageSerializer
import traceback

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])  # anyone can send a message
def messages_list_create(request):
    try:
        if request.method == 'GET':
            messages = Message.objects.all().order_by('-id')
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = MessageSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # Log error to a file so you can debug on Render free plan
        with open("messages_error.log", "a") as f:
            f.write(traceback.format_exc())
            f.write("\n\n")
        return Response({"error": "Internal server error"}, status=500)
