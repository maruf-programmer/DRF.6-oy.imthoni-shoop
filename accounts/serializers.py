from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from .models import CustomUser, VIA_EMAIL, VIA_PHONE
from shared.utility import check_email_or_phone
from shared.utils import send_to_mail
from django.utils import timezone
from .models import CodeVerify, CHANGE_INFO, DONE
from django.contrib.auth.password_validation import validate_password


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Misol (email)",
            value={"email_or_phone": "user@example.com"},
            request_only=True,
        ),
        OpenApiExample(
            "Misol (telefon)",
            value={"email_or_phone": "+998901234567"},
            request_only=True,
        ),
    ]
)
class SignUpSerializer(serializers.ModelSerializer):
    email_or_phone = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Email yoki telefon raqam (masalan: user@example.com yoki +998901234567)",
    )

    class Meta:
        model = CustomUser
        fields = ["id", "auth_type", "auth_status", "email_or_phone"]
        read_only_fields = ["auth_type", "auth_status"]

    # validate, create, to_representation o‘zgarishsiz qoladi (oldingi kod bilan bir xil)
    def validate(self, attrs):
        user_input = attrs.get("email_or_phone", "")
        field_type, cleaned_value = check_email_or_phone(user_input)

        if field_type == "email":
            if CustomUser.objects.filter(email=cleaned_value).exists():
                raise ValidationError(
                    {"email_or_phone": "Bu email manzili allaqachon ro'yxatdan o'tgan!"}
                )
            attrs["email"] = cleaned_value
            attrs["auth_type"] = VIA_EMAIL

        elif field_type == "phone":
            if CustomUser.objects.filter(phone_number=cleaned_value).exists():
                raise ValidationError(
                    {"email_or_phone": "Bu telefon raqami allaqachon ro'yxatdan o'tgan!"}
                )
            attrs["phone_number"] = cleaned_value
            attrs["auth_type"] = VIA_PHONE

        attrs.pop("email_or_phone", None)
        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create(**validated_data)

        if user.auth_type == VIA_EMAIL:
            code = user.create_code(VIA_EMAIL)
            send_to_mail(user.email, code)
            print(f"Email code: {code}")

        elif user.auth_type == VIA_PHONE:
            code = user.create_code(VIA_PHONE)
            # send_phone(user.phone_number, code)
            print(f"Phone code: {code}")

        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["token"] = instance.token()
        return data


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Misol (email)",
            value={"email_or_phone": "user@example.com", "code": "1234"},
            request_only=True,
        ),
    ]
)
class VerifyCodeSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Email yoki telefon raqam (ro'yxatdan o'tishdagi bilan bir xil)",
    )
    code = serializers.CharField(
        max_length=4,
        required=True,
        write_only=True,
        help_text="Email/SMS orqali kelgan 4 xonali kod",
    )

    def validate(self, attrs):
        user_input = attrs.get("email_or_phone", "")
        code = attrs.get("code", "").strip()

        field_type, cleaned_value = check_email_or_phone(user_input)

        if field_type == "email":
            user = CustomUser.objects.filter(email=cleaned_value).first()
        else:
            user = CustomUser.objects.filter(phone_number=cleaned_value).first()

        if not user:
            raise ValidationError({"message": "User not found!"})

        verify_code = (
            CodeVerify.objects.filter(user=user, code=code, is_used=False)
            .order_by("-created_at")
            .first()
        )

        if not verify_code:
            raise ValidationError({"code": "Verification code is incorrect!"})

        if verify_code.expiration_time and verify_code.expiration_time < timezone.now():
            raise ValidationError({"code": "Code has expired!"})

        attrs["user"] = user
        attrs["verify_code"] = verify_code
        return attrs


class ResendCodeSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Email yoki telefon raqam",
    )

    def validate(self, attrs):
        user_input = attrs.get("email_or_phone", "")
        field_type, cleaned_value = check_email_or_phone(user_input)

        if field_type == "email":
            user = CustomUser.objects.filter(email=cleaned_value).first()
        else:
            user = CustomUser.objects.filter(phone_number=cleaned_value).first()

        if not user:
            raise ValidationError({"message": "User not found!"})

        active_code = (
            CodeVerify.objects.filter(
                user=user, is_used=False, expiration_time__gte=timezone.now()
            )
            .order_by("-created_at")
            .first()
        )

        if active_code:
            raise ValidationError(
                {
                    "message": f"You still have an active code valid until {active_code.expiration_time}"
                }
            )

        attrs["user"] = user
        return attrs


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Misol",
            value={
                "first_name": "Ali",
                "last_name": "Valiyev",
                "password": "strong123",
                "confirm_password": "strong123",
                "user_role": "ordinary_user",
            },
            request_only=True,
        ),
    ]
)
class ChangeProfileInfoSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password],
        help_text="Yangi parol (kamida 8 belgi, raqam va harf)"
    )
    confirm_password = serializers.CharField(
        write_only=True, required=True,
        help_text="Parolni tasdiqlash (yuqoridagi parol bilan bir xil bo'lishi kerak)"
    )
    first_name = serializers.CharField(required=True, max_length=100, help_text="Ism")
    last_name = serializers.CharField(required=True, max_length=100, help_text="Familiya")
    user_role = serializers.CharField(
        required=True, max_length=100,
        help_text="Rol: ordinary_user (oddiy), seller (sotuvchi), admin (administrator)"
    )

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "password",
            "confirm_password",
            "user_role",
        ]

    def validate(self, attrs):
        if (
            attrs["password"]
            and attrs["confirm_password"]
            and attrs["password"] != attrs["confirm_password"]
        ):
            raise ValidationError({"password": "Passwords do not match!"})
        return attrs

    def update(self, instance, validated_data):
        validated_data.pop("confirm_password", None)
        password = validated_data.pop("password", None)

        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.user_role = validated_data.get("user_role", instance.user_role)

        if password:
            instance.set_password(password)

        instance.auth_status = CHANGE_INFO
        instance.save()
        return instance

    def to_representation(self, instance):
        user = super().to_representation(instance)
        user["token"] = instance.token()
        return user


class UploadProfilePhotoSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=True, help_text="Profil uchun rasm (jpg, png)")

    class Meta:
        model = CustomUser
        fields = ["photo"]

    def update(self, instance, validated_data):
        instance.photo = validated_data.get("photo", instance.photo)
        instance.auth_status = DONE
        instance.save()
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False, allow_null=True, help_text="Foydalanuvchi rasmi")

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "photo",
            "user_role"
        ]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False, allow_null=True, help_text="Yangi rasm yuklash (ixtiyoriy)")

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "user_role", "photo"]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
            "user_role": {"required": False},
        }

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.user_role = validated_data.get("user_role", instance.user_role)

        if "photo" in validated_data:
            instance.photo = validated_data.get("photo")

        instance.save()
        return instance


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Misol (email)",
            value={"email_or_phone": "user@example.com", "password": "mypassword"},
            request_only=True,
        ),
    ]
)
class LoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(
        required=True, write_only=True,
        help_text="Email yoki telefon raqam"
    )
    password = serializers.CharField(
        required=True, write_only=True,
        help_text="Parol"
    )

    def validate(self, attrs):
        user_input = attrs.get("email_or_phone", "")
        password = attrs.get("password", "")
        field_type, cleaned_value = check_email_or_phone(user_input)

        if field_type == "email":
            user = CustomUser.objects.filter(email=cleaned_value).first()
        else:
            user = CustomUser.objects.filter(phone_number=cleaned_value).first()

        if not user or not user.check_password(password):
            raise ValidationError({"message": "Email/phone or password is incorrect"})

        attrs["user"] = user
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(
        required=True, write_only=True,
        help_text="Parolni tiklash uchun email yoki telefon"
    )

    def validate(self, attrs):
        user_input = attrs.get("email_or_phone", "")
        field_type, cleaned_value = check_email_or_phone(user_input)

        if field_type == "email":
            user = CustomUser.objects.filter(email=cleaned_value).first()
            verify_type = VIA_EMAIL
        else:
            user = CustomUser.objects.filter(phone_number=cleaned_value).first()
            verify_type = VIA_PHONE

        if not user:
            raise ValidationError({"message": "User not found!"})

        attrs["user"] = user
        attrs["verify_type"] = verify_type
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(
        required=True, write_only=True,
        help_text="Email yoki telefon"
    )
    code = serializers.CharField(
        max_length=4, required=True, write_only=True,
        help_text="Tasdiqlash kodi"
    )
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password],
        help_text="Yangi parol"
    )
    confirm_password = serializers.CharField(
        write_only=True, required=True,
        help_text="Yangi parolni tasdiqlang"
    )

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise ValidationError({"confirm_password": "Passwords do not match!"})

        user_input = attrs.get("email_or_phone", "")
        code = attrs.get("code", "").strip()

        field_type, cleaned_value = check_email_or_phone(user_input)

        if field_type == "email":
            user = CustomUser.objects.filter(email=cleaned_value).first()
            verify_type = VIA_EMAIL
        else:
            user = CustomUser.objects.filter(phone_number=cleaned_value).first()
            verify_type = VIA_PHONE

        if not user:
            raise ValidationError({"message": "User not found!"})

        verify_code = CodeVerify.objects.filter(
            user=user,
            verify_type=verify_type,
            code=code,
            is_used=False,
        ).order_by("-created_at").first()

        if not verify_code:
            raise ValidationError({"code": "Verification code is incorrect!"})

        from django.utils import timezone

        if verify_code.expiration_time and verify_code.expiration_time < timezone.now():
            raise ValidationError({"code": "The code has expired!"})

        attrs["user"] = user
        attrs["verify_code"] = verify_code
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        required=True, write_only=True,
        help_text="Eski parol"
    )
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password],
        help_text="Yangi parol"
    )
    confirm_password = serializers.CharField(
        write_only=True, required=True,
        help_text="Yangi parolni tasdiqlang"
    )

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if not user:
            raise ValidationError({"message": "Authentication required"})

        if attrs["new_password"] != attrs["confirm_password"]:
            raise ValidationError({"confirm_password": "Passwords do not match!"})

        if not user.check_password(attrs["old_password"]):
            raise ValidationError({"old_password": "Old password is incorrect"})

        attrs["user"] = user
        return attrs