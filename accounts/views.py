from django.shortcuts import render
from .serializers import UserSerializer, UserLoginSerializer, FriendRequestSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

from .models import User, FriendRequest
from django.db.models import Q
from datetime import datetime, timedelta


# Create your views here.

class UserCreateApiView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        print("request.data", request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_token = get_tokens_for_user(user)
            return Response({"token":user_token,"msg":"User Register Succefully"}, status=201)
      
        return Response(serializer.errors, status=400)
    

class UserLoginApiView(APIView):
    """User Login"""
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserLoginSerializer(data = request.data)
        print("request.data = ", request.data)  #request.data =  {'email': 'xyz@gmail.com', 'password': 'xyz'}
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get("email")
        password = serializer.data.get("password")
        print("email = ", email)
        print("password = ", password)
        user = authenticate(email=email, password=password)

        if user is not None:
            user_token = get_tokens_for_user(user)
            return Response({"token":user_token,"message": "Logged in successfully."}, status=200)
        else:
            return Response({"message": "No user found."}, status=404)
                


class UserListApiView(APIView):
    def get(self, request):
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data, status=200)






class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, user_id):
        from_user = request.user

        try:
            to_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"msg": "User does not exist"}, status=404) 

        if from_user.id == to_user.id:
            return Response({"msg":"You cannot send friend request to yourself"}, status=400)

        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response({"msg":"Friend request already sent"}, status=400)
        
        # check more than 3 friend requests within a day
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        recent_requests = FriendRequest.objects.filter(from_user=from_user, timestamp__gte=one_minute_ago)
        if recent_requests.count() >= 3:
            return Response({'detail': 'You cannot send more than 3 friend requests within a day.'}, status=429)


        friend_request = FriendRequest.objects.create(from_user=from_user, to_user=to_user)
        return Response({"msg":"Friend request sent successfully"}, status=201)
    


class RespondFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, friend_request_id, action):
        try:
            print("request.user = ",request.user.id)
            print("friend_request_id = ",friend_request_id)
            friend_request = FriendRequest.objects.get(from_user=friend_request_id, to_user=request.user.id)
        except FriendRequest.DoesNotExist:
            return Response({"msg": "Friend request not found"}, status=404)
        
        if action not in ['accept', 'reject']:
            return Response({"msg": "Invalid action. It should be Accept or reject only."}, status=400)
        
        if action == 'accept':
            friend_request.status = 'accepted'
            friend_request.save()
            return Response({"msg":"Friend request accepted successfully"}, status=200)
        elif action == 'reject':
            friend_request.status = 'rejected'
            friend_request.save()

        return Response({"msg":"Friend request rejected successfully"}, status=200)




class ListPendingRequestsView(ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user, status='pending')
    



class ListFriendsView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(
            Q(sent_requests__to_user=self.request.user, sent_requests__status='accepted') |
            Q(received_requests__from_user=self.request.user, received_requests__status='accepted')
        ).distinct()
    


class UserSearchView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        keyword = self.request.query_params.get('q', '')
        return User.objects.filter(
            Q(email__iexact=keyword) |
            Q(first_name__icontains=keyword) 
           
        ).distinct()

    pagination_class = PageNumberPagination
    pagination_class.page_size = 10




class ListFriendsView(ListAPIView):
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(
            Q(sent_requests__status='accepted') |
            Q(received_requests__status='accepted')
        ).distinct()
    


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }