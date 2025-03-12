from django.contrib.auth import get_user_model
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import filters
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny

from accounts.serializers import SignupSerializer, UserListSerializer

User = get_user_model()


# Create your views here.
class SignupView(CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]


@extend_schema(
    summary="List Users",
    description="""
    Retrieves a list of users who are **not staff** and excludes the currently authenticated user.

    Supports **search by email or ID** using the `search` query parameter.
    """,
    parameters=[
        OpenApiParameter(
            name="search",
            description="Search users by email or ID",
            required=False,
            type=str
        )
    ],
    responses={200: UserListSerializer(many=True)}
)
class UserListView(ListAPIView):
    serializer_class = UserListSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('email', 'id')

    def get_queryset(self):
        qs = User.objects.filter(Q(is_staff=False,), ~Q(id=self.request.user.id))
        return qs