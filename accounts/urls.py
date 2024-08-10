from django.urls import path
from .views import *
urlpatterns = [

    path('users/', UserListApiView.as_view(), name='user_list'),
    path('users/create/', UserCreateApiView.as_view(), name='user_create'),
    path('users/login/', UserLoginApiView.as_view(), name='user_login'),

    path('send-friend-request/<int:user_id>/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('respond-friend-request/<int:friend_request_id>/<str:action>/', RespondFriendRequestView.as_view(), name='respond-friend-request'  ),
    path('pending-requests/', ListPendingRequestsView.as_view(), name='pending-requests'),
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('friends-list/', ListFriendsView.as_view(), name='list-friends'),
]
