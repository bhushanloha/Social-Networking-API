from rest_framework import serializers
from .models import User,FriendRequest


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id','email','first_name','last_name',"password"]
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
     

        if not email:
            raise serializers.ValidationError("Email is required.")
        
        if not password:
            raise serializers.ValidationError("Password is required.")
        
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already exists.")
        
        return data
        

    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    

class UserLoginSerializer(serializers.ModelSerializer):
    """Serializer for user login."""
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['email', 'password']



class FriendRequestSerializer(serializers.ModelSerializer):
    """Serializer for FriendRequest model."""
    from_user = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'timestamp', 'status']