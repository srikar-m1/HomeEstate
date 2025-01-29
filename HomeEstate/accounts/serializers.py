from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name')


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        extra_kwargs = {
            'password': {'required': True},
            'country_code': {'required': True},
            'mobile_num': {'required': True},
        }

    def validate(self, attrs):
        email = attrs.get('email',).strip().lower()
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('User already exists.')
        return attrs

    def create(self, validated_data):
        # Ensure the password is hashed when creating the user
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'mobile_num', 'country_code', 'password']
        extra_kwargs = {
            'password': {'write_only': True}  # Only write password, don't include it in GET requests
        }

    def update(self, instance, validated_data):
        # Check if the password is provided and hash it if necessary
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)  # Hash the password
            validated_data['password'] = instance.password  # Ensure password is updated

        # Update the other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get('email').lower()
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError('please enter both the email and password')

        if not CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('user does not exist')

        user = authenticate(request=self.context.get('request'), email=email, password=password)

        if not user:
            raise serializers.ValidationError('you have entered a wrong email or password')

        attrs['user'] = user
        return attrs
