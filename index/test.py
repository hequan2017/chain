from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()
user = request.user.username
result_all = "123"
async_to_sync(channel_layer.group_send)(user, {"type": "user.message",
                                               'text': result_all})