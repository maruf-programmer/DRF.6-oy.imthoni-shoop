from django.shortcuts import render
from .models import VIA_EMAIL, VIA_PHONE, SELLER, ORDINARY_USER, CODE_VERIFY, CHANGE_INFO
from rest_framework.generics import CreateAPIView
from rest_framework import permissions
from .serializers import SignUpSerializer, VerifyCodeSerializer, ResendCodeSerializer
from .models import CustomUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from shared.utils import send_to_mail
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser


class SignUpView(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SignUpSerializer
    queryset = CustomUser.objects.all()


class VerifyCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = VerifyCodeSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            verify_code = serializer.validated_data['verify_code']

            verify_code.is_used = True
            verify_code.save()

            user.auth_status = CODE_VERIFY
            user.save()

            return Response({
                "success": True,
                "message": "Account successfully verified.",
                "auth_status": user.auth_status,
                "tokens": user.token()
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ResendCodeSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']

            code = user.create_code(user.auth_type)

            if user.auth_type == VIA_EMAIL:
                send_to_mail(
                    message=f"Your new verification code: {code}",
                    email=user.email,
                )

            elif user.auth_type == VIA_PHONE:
                print(f"New phone code: {code}")

            return Response({
                "success": True,
                "message": "A new verification code has been sent."
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from .serializers import ChangeProfileInfoSerializer, UploadProfilePhotoSerializer


class ChangeProfileInfoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user

        if user.auth_status != CODE_VERIFY:
            return Response(
                {"message": "You must verify the code first!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ChangeProfileInfoSerializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Name and passwords saved successfully. Now upload a picture.",
                "auth_status": user.auth_status
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UploadProfilePhotoView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, *args, **kwargs):
        user = request.user

        if user.auth_status != CHANGE_INFO:
            return Response(
                {"message": "You must first enter your full name and passwords."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UploadProfilePhotoSerializer(instance=user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Registration completed successfully!",
                "auth_status": user.auth_status
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)