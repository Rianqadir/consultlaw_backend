import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Message, Notification
from .serializers import MessageSerializer, NotificationSerializer


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
        return await Message.objects.acreate(
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content
        )


# This function can be safely imported and called inside a view or signal
async def send_notification(user_id, content):
    notification = await Notification.objects.acreate(
        user_id=user_id,
        content=content
    )

    layer = get_channel_layer()
    await layer.group_send(
        f"user_{user_id}",
        {
            "type": "notify",
            "notification": NotificationSerializer(notification).data
        }
    )

# ❌ Removed invalid 'await send_notification(...)' from global scope!
# ✅ Instead, import and use this function inside a view using:
#     from accounts.consumers import send_notification
#     async_to_sync(send_notification)(...)
