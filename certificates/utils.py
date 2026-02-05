# certificates/utils.py
import requests
import json
from django.conf import settings
from django.core.mail import send_mail

def send_httpsms_reminder(to_number, name, cert_type, parent_name=None):
    url = 'https://api.httpsms.com/v1/messages/send'
    api_key = settings.HTTPSMS_API_KEY
    from_number = settings.HTTPSMS_FROM_NUMBER
    
    headers = {
        'x-api-key': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    # SMS Logic: Concise but special
    if "Dedication" in cert_type and parent_name:
        content = f"Dear {parent_name}, the dedication certificate for {name} is ready for collection at Newlife Church office. We celebrate with you! God bless you."
    else:
        content = f"Congratulations {name}! Your baptism certificate is ready for collection at Newlife Church clerk's office. We look forward to seeing you. Welcome to the Newlife SDA Family."

    payload = {
        "content": content,
        "from": from_number,
        "to": to_number
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"⚠️ SMS Connection Error: {e}")
        return False

def send_church_email(recipient_email, name, cert_type, parent_name=None):
    if not recipient_email:
        return False
    
    if "Dedication" in cert_type and parent_name:
        subject = f"Congratulations! Child Dedication Certificate Ready - {name}"
        message = (
            f"Dear {parent_name},\n\n"
            f"Greetings in the name of our Lord Jesus Christ!\n\n"
            f"We are delighted to inform you that the Child Dedication certificate for {name} is ready. "
            f"It was such a blessing to have your family participate in this sacred milestone at Newlife SDA Church.\n\n"
            f"Please visit the clerk's office at your earliest convenience to pick up the certificate.\n\n"
            f"May God continue to grant you wisdom and grace as you raise {name} in the ways of the Lord.\n\n"
            f"Blessings,\n"
            f"Newlife Church Administration"
        )
    else:
        subject = f"Your Baptism Certificate is Ready! - {name}"
        message = (
            f"Dear {name},\n\n"
            f"Congratulations on your baptism! We rejoice with you as you take this significant step in your walk with Christ.\n\n"
            f"We are pleased to inform you that your baptism certificate has been processed and is ready for collection at the clerk's office.\n\n"
            f"We look forward to seeing you soon and continuing this journey of faith together.\n\n"
            f"Grace and Peace,\n"
            f"Newlife Church Administration"
        )
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False