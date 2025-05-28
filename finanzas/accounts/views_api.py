from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class HelloJWTView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"mensaje": f"Hola {request.user.first_name}, estás autenticado con JWT."})
