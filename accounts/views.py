from django.shortcuts import render
from rest_framework import status, generics, filters, permissions, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from asgiref.sync import async_to_sync
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from datetime import date
from .models import Booking
from .serializers import BookingSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Booking
from .serializers import BookingSerializer
from django.conf import settings
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from .models import Booking
from .serializers import BookingSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Booking
from .serializers import BookingSerializer
from datetime import datetime

import stripe

from .models import (
    User, LawyerProfile, Availability, Booking, Message, Notification
)
from .serializers import (
    RegisterSerializer, LoginSerializer, LawyerProfileSerializer,
    LawyerListSerializer, AvailabilitySerializer, BookingSerializer,
    MessageSerializer, NotificationSerializer
)
from .assistant import triage_issue
from .consumers import send_notification

stripe.api_key = settings.STRIPE_SECRET_KEY

# -------------------- Auth -------------------- #

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
            return Response({"detail": "Invalid credentials"}, status=401)

        if not user.check_password(password):
            return Response({"detail": "Invalid credentials"}, status=401)

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
        })


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

# -------------------- Lawyer Profile -------------------- #

class LawyerProfileCreateView(generics.CreateAPIView):
    serializer_class = LawyerProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'lawyer':
            raise PermissionDenied("Only lawyers can create a profile.")
        serializer.save(user=self.request.user)


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

# -------------------- Lawyers Public Listing -------------------- #

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

# -------------------- Availability -------------------- #

class AvailabilityCreateView(generics.CreateAPIView):
    serializer_class = AvailabilitySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'lawyer':
            raise PermissionDenied("Only lawyers can set availability.")
        serializer.save(lawyer=self.request.user)


class AvailabilityListView(generics.ListAPIView):
    serializer_class = AvailabilitySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        lawyer_id = self.request.query_params.get('lawyer')
        if lawyer_id:
            return Availability.objects.filter(lawyer_id=lawyer_id)
        return Availability.objects.none()

# -------------------- Booking -------------------- #

class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'client'


class BookingCreateView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsClient]

    def perform_create(self, serializer):
        lawyer = serializer.validated_data['lawyer']
        date = serializer.validated_data['date']
        time = serializer.validated_data['time']

        if lawyer.role != 'lawyer':
            raise serializers.ValidationError("You can only book a lawyer.")

        weekday = date.strftime('%A')
        availabilities = Availability.objects.filter(
            lawyer=lawyer,
            day_of_week=weekday,
            start_time__lte=time,
            end_time__gte=time
        )

        if not availabilities.exists():
            raise serializers.ValidationError("Lawyer is not available at this time.")

        serializer.save(client=self.request.user, status='pending')
        async_to_sync(send_notification)(
            lawyer.id,
            f"New booking from {self.request.user.get_full_name()} for {date} at {time}"
        )


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


class LawyerDashboardView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role != 'lawyer':
            return Booking.objects.none()
        return Booking.objects.filter(lawyer=user, status='confirmed').order_by('date', 'time')

# -------------------- Payment -------------------- #

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_intent(request):
    booking_id = request.data.get("booking_id")

    try:
        booking = Booking.objects.get(id=booking_id, client=request.user)
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)

    if booking.status != 'pending':
        return Response({"error": "Booking already paid or cancelled"}, status=400)

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

# -------------------- AI Assistant -------------------- #

@api_view(['POST'])
@permission_classes([AllowAny])
def assistant_triage(request):
    issue = request.data.get('description', '')
    if not issue:
        return Response({"error": "No description provided"}, status=400)
    suggestion = triage_issue(issue)
    return Response({"suggestion": suggestion})

# -------------------- Messaging -------------------- #

class SendMessageView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        recipient = serializer.validated_data['recipient']
        if self.request.user == recipient:
            raise serializers.ValidationError("You cannot message yourself.")
        message = serializer.save(sender=self.request.user)
        async_to_sync(send_notification)(
            recipient.id,
            f"You have a new message from {self.request.user.get_full_name()}"
        )


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

# -------------------- Notifications -------------------- #

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-timestamp')



class MyBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        filter_type = request.query_params.get("filter", "all")
        now = datetime.now()

        if filter_type == "upcoming":
            bookings = Booking.objects.filter(client=user, date__gte=now.date()).order_by('date')
        elif filter_type == "past":
            bookings = Booking.objects.filter(client=user, date__lt=now.date()).order_by('-date')
        else:
            bookings = Booking.objects.filter(client=user).order_by('-date')

        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


# accounts/views.py


class MyBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        filter_param = request.GET.get('filter', 'all')

        if user.role != 'Client':
            return Response({"detail": "Only clients can view this."}, status=403)

        bookings = Booking.objects.filter(client=user)

        # Apply filtering
        if filter_param == "upcoming":
            bookings = bookings.filter(date__gte=datetime.today()).order_by("date")
        elif filter_param == "past":
            bookings = bookings.filter(date__lt=datetime.today()).order_by("-date")

        serialized = BookingSerializer(bookings, many=True)
        return Response(serialized.data)


# views.py


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lawyer_dashboard_view(request):
    user = request.user
    if user.role != 'Lawyer':
        return Response({'error': 'Only lawyers can access this view.'}, status=403)

    today = date.today()
    bookings = Booking.objects.filter(
        lawyer=user,
        date__gte=today
    ).order_by('date', 'time')

    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)



class LawyerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # already implemented
        pass

    @action(detail=False, methods=['post'])
    def cancel_booking(self, request):
        booking_id = request.data.get('booking_id')
        reason = request.data.get('reason', 'Cancelled by lawyer')

        try:
            booking = Booking.objects.get(id=booking_id, lawyer=request.user)

            if booking.status in ['cancelled', 'rejected']:
                return Response({"error": "Booking already cancelled or rejected."}, status=400)

            booking.status = 'cancelled'
            booking.save()

            # Optionally notify client
            from .consumers import send_notification
            import asyncio
            asyncio.create_task(send_notification(
                user_id=booking.client.id,
                content=f"Your booking on {booking.date} at {booking.time} was cancelled. Reason: {reason}"
            ))

            return Response({"message": "Booking cancelled successfully."})
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found or unauthorized."}, status=404)