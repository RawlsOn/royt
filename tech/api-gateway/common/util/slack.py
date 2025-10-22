import os, time, re, json
from django.conf import settings
from django.utils import timezone

from slack_sdk import WebClient
client = WebClient(token=settings.SLACK_BOT_TOKEN)

def fire_text(text):
    if settings.RUNNING_ENV == 'test':
        return

    channel = settings.SLACK_CHANNEL_ID

    client.chat_postMessage(
        channel= channel,
        text= text,
    )

def fire(payload, keys=None, kors=None):
    dict_to_work = {}
    if keys is not None:
        for key, val in payload.items():
            if key in keys: dict_to_work[key] = val
    else:
        dict_to_work = payload

    fields = []
    for key, val in dict_to_work.items():
        out_key = key
        if kors is not None:
            out_key = kors[key]
        fields.append({
            'type': 'mrkdwn',
            'text': ('').join([
                '*' + out_key + '*\n',
                str(val)
            ])
        })
    blocks = [
        {
            "type": "section",
            "fields": [{
                'type': 'mrkdwn',
                'text': ''.join([
                    '[' + settings.RUNNING_ENV + '/',
                    settings.SERVICE_NAME + ']',
                    timezone.now().strftime("%Y-%m-%d %H:%M:%S")
                ])
            }]
        },
        {
            "type": "section",
            "fields": fields
        }
    ]

    if settings.RUNNING_ENV == 'test':
        return

    channel = settings.SLACK_CHANNEL_ID
    client.chat_postMessage(
        channel= channel,
        text= json.dumps(blocks),
        blocks= json.dumps(blocks)
    )



