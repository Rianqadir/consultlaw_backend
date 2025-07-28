from django.urls import path
from .views import (
    RegisterView, LoginView, MeView,
    LawyerProfileCreateView, LawyerProfileCreateUpdateView, PublicLawyerListView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', MeView.as_view(), name='me'),

    # Lawyer profile routes
    path('lawyer/profile/create/', LawyerProfileCreateView.as_view(), name='lawyer-profile-create'),
    path('lawyer/profile/', LawyerProfileCreateUpdateView.as_view(), name='lawyer-profile-view-update'),
]


urlpatterns += [
    path('lawyers/', PublicLawyerListView.as_view(), name='lawyer-list'),
]

from .views import BookingCreateView, BookingListView

urlpatterns += [
    path('bookings/', BookingListView.as_view(), name='booking-list'),
    path('bookings/create/', BookingCreateView.as_view(), name='booking-create'),
]

from .views import AvailabilityCreateView, AvailabilityListView

urlpatterns += [
    path('availability/create/', AvailabilityCreateView.as_view(), name='create-availability'),
    path('availability/', AvailabilityListView.as_view(), name='lawyer-availability'),
]

from .views import create_payment_intent

urlpatterns += [
    path('payments/create-intent/', create_payment_intent, name='create-payment-intent'),
]

from .views import assistant_triage

urlpatterns += [
    path('assistant/triage/', assistant_triage, name='assistant-triage'),
]

from .views import SendMessageView, ConversationView

urlpatterns += [
    path('messages/send/', SendMessageView.as_view(), name='send-message'),
    path('messages/conversation/', ConversationView.as_view(), name='view-conversation'),
]

from .views import NotificationListView

urlpatterns += [
    path('notifications/', NotificationListView.as_view(), name='notifications'),
]

from .views import LawyerDashboardView

urlpatterns += [
    path('lawyer/dashboard/', LawyerDashboardView.as_view(), name='lawyer-dashboard'),
]
