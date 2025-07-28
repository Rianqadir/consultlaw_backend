from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import NotificationSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer
from rest_framework import serializers
from .models import User
from .serializers import AvailabilitySerializer
import stripe
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .assistant import triage_issue
from .models import Message
from .serializers import MessageSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import Booking
from .serializers import BookingSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        }, status=status.HTTP_200_OK)
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "address": user.address,
        }
        return Response(data)


from .models import LawyerProfile
from .serializers import LawyerProfileSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class LawyerProfileCreateUpdateView(generics.RetrieveUpdateAPIView):
    queryset = LawyerProfile.objects.all()
    serializer_class = LawyerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return self.request.user.lawyer_profile
        except LawyerProfile.DoesNotExist:
            raise PermissionDenied("Profile does not exist. Create it first.")

    def perform_update(self, serializer):
        if self.request.user.role != 'lawyer':
            raise PermissionDenied("Only lawyers can update profile.")
        serializer.save(user=self.request.user)

class LawyerProfileCreateView(generics.CreateAPIView):
    serializer_class = LawyerProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'lawyer':
            raise PermissionDenied("Only lawyers can create a profile.")
        serializer.save(user=self.request.user)

from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import LawyerListSerializer

class PublicLawyerListView(generics.ListAPIView):
    queryset = User.objects.filter(role='lawyer', lawyer_profile__isnull=False)
    serializer_class = LawyerListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        'lawyer_profile__specialties': ['icontains'],
        'lawyer_profile__languages': ['icontains'],
        'lawyer_profile__fee': ['gte', 'lte'],
    }

    search_fields = ['first_name', 'last_name', 'lawyer_profile__specialties']

from .models import Booking
from .serializers import BookingSerializer
from rest_framework import permissions

class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'client'

class BookingCreateView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsClient]

    def perform_create(self, serializer):
        lawyer = serializer.validated_data['lawyer']
        if lawyer.role != 'lawyer':
            raise serializers.ValidationError("You can only book a lawyer.")
        serializer.save(client=self.request.user, status='pending')

class BookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'client':
            return Booking.objects.filter(client=user)
        elif user.role == 'lawyer':
            return Booking.objects.filter(lawyer=user)
        return Booking.objects.none()

class AvailabilityCreateView(generics.CreateAPIView):
    serializer_class = AvailabilitySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'lawyer':
            raise PermissionDenied("Only lawyers can set availability.")
        serializer.save(lawyer=self.request.user)



class AvailabilityListView(generics.ListAPIView):
    serializer_class = AvailabilitySerializer
    permission_classes = [AllowAny]  # Publicly visible

    def get_queryset(self):
        lawyer_id = self.request.query_params.get('lawyer')
        if lawyer_id:
            return Availability.objects.filter(lawyer_id=lawyer_id)
        return Availability.objects.none()

class BookingCreateView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsClient]

    def perform_create(self, serializer):
        lawyer = serializer.validated_data['lawyer']
        date = serializer.validated_data['date']
        time = serializer.validated_data['time']

        if lawyer.role != 'lawyer':
            raise serializers.ValidationError("You can only book a lawyer.")

        # Validate availability
        weekday = date.strftime('%A')
        availabilities = Availability.objects.filter(
            lawyer=lawyer,
            day_of_week=weekday,
            start_time__lte=time,
            end_time__gte=time
        )

        if not availabilities.exists():
            raise serializers.ValidationError("Lawyer is not available at this time.")

        # ✅ THIS IS IMPORTANT: sets client and default status
        serializer.save(client=self.request.user, status='pending')




stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_intent(request):
    """
    Expects:
    {
      "booking_id": 1
    }
    Returns:
    {
      "clientSecret": "pi_123_secret_456",
      "booking_id": 1
    }
    """
    from .models import Booking

    booking_id = request.data.get("booking_id")

    try:
        booking = Booking.objects.get(id=booking_id, client=request.user)
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)

    if booking.status != 'pending':
        return Response({"error": "Booking already paid or cancelled"}, status=400)

    # Stripe needs amount in paisa (100x)
    amount = int(Decimal(booking.fee) * 100)

    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency='pkr',
        metadata={'integration_check': 'accept_a_payment'},
    )

    return Response({
        "clientSecret": intent['client_secret'],
        "booking_id": booking_id
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def assistant_triage(request):
    issue = request.data.get('description', '')
    if not issue:
        return Response({"error": "No description provided"}, status=400)
    
    suggestion = triage_issue(issue)
    return Response({"suggestion": suggestion})



class SendMessageView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        recipient = serializer.validated_data['recipient']
        if self.request.user == recipient:
            raise serializers.ValidationError("You cannot message yourself.")
        serializer.save(sender=self.request.user)

class ConversationView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        other_user_id = self.request.query_params.get('user')
        if not other_user_id:
            return Message.objects.none()

        return Message.objects.filter(
            (models.Q(sender=self.request.user, recipient_id=other_user_id) |
             models.Q(sender_id=other_user_id, recipient=self.request.user))
        ).order_by('timestamp')

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-timestamp')

class LawyerDashboardView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role != 'lawyer':
            return Booking.objects.none()

        return Booking.objects.filter(
            lawyer=user,
            status='confirmed'
        ).order_by('date', 'time')