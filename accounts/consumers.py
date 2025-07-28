import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message
from .serializers import MessageSerializer
from django.contrib.auth.models import AnonymousUser

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if self.user is None or isinstance(self.user, AnonymousUser):
            await self.close()
        else:
            self.room_group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        recipient_id = data.get('recipient')
        content = data.get('content')

        # Save message in DB
        message = await self.save_message(self.user.id, recipient_id, content)
        serialized = MessageSerializer(message)

        # Send to recipient's group
        await self.channel_layer.group_send(
            f"user_{recipient_id}",
            {
                "type": "chat_message",
                "message": serialized.data
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    async def notify(self, event):
    await self.send(text_data=json.dumps({
        "type": "notification",
        "data": event["notification"]
    }))


    @staticmethod
    async def save_message(sender_id, recipient_id, content):
        return await Message.objects.acreate(sender_id=sender_id, recipient_id=recipient_id, content=content)

from .models import Notification
from .serializers import NotificationSerializer

async def send_notification(user_id, content):
    # Save to DB
    notification = await Notification.objects.acreate(user_id=user_id, content=content)

    # Broadcast to WebSocket
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    layer = get_channel_layer()
    await layer.group_send(
        f"user_{user_id}",
        {
            "type": "notify",
            "notification": NotificationSerializer(notification).data
        }
    )

from accounts.consumers import send_notification

# When booking is confirmed:
await send_notification(
    user_id=booking.lawyer.id,
    content=f"New booking from {booking.client.get_full_name()} for {booking.date} at {booking.time}"
)
