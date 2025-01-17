from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Department


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'user_type', 'department')
        read_only_fields = ('id', 'user_type')

class BaseSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        required=False
    )

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 
                 'first_name', 'last_name', 'department')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2', None)
        password = validated_data.pop('password')
        
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        return user

class ManagerSignupSerializer(BaseSignupSerializer):
    def create(self, validated_data):
        validated_data['user_type'] = 'MANAGER'
        return super().create(validated_data)

class EmployeeSignupSerializer(BaseSignupSerializer):
    manager = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(user_type='MANAGER'),
        required=True
    )

    class Meta(BaseSignupSerializer.Meta):
        fields = BaseSignupSerializer.Meta.fields + ('manager',)

    def create(self, validated_data):
        validated_data['user_type'] = 'EMPLOYEE'
        return super().create(validated_data)
    


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()



class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description']


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'department']
        
    

        
