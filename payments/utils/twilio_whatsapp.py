from twilio.rest import Client
from django.conf import settings

def send_whatsapp_message(to_number, message):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    message = client.messages.create(
        from_=settings.TWILIO_WHATSAPP_NUMBER,
        body=message,
        to=f'whatsapp:{to_number}'
    )
    return message.sid
