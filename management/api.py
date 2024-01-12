from rest_framework.views import APIView
from .models import Complain
from .serializer import ComplainSerializer
from rest_framework.response import Response

class ComplainDetails(APIView):
    def get(self, request, complain_id):
        complaint = Complain.objects.get(id=complain_id)
        serializer = ComplainSerializer(complaint)
        return Response(serializer.data)