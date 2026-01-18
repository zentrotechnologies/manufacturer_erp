
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from io import BytesIO
from django.core.files.storage import FileSystemStorage
import time
from .validations import hosturl
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from manufacturer_erp.settings import *
import locale
from urllib.parse import urlparse, parse_qs
from datetime import datetime,date,timedelta
from PIL import Image, ImageDraw, ImageFont
from mimetypes import guess_type
from django.conf import settings
import logging
from django.utils.text import slugify

import re
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

def format_indian_rupees(number):
    """
    Format number in Indian numbering system without using locale
    """
    try:
        number = int(number)
        
        # Handle negative numbers
        sign = '-' if number < 0 else ''
        number = abs(number)
        
        if number == 0:
            return '0'
        
        # Convert to string and process
        num_str = str(number)
        length = len(num_str)
        
        # Indian numbering system: grouped as 3,2,2,...
        if length <= 3:
            return f"{sign}{num_str}"
        
        # Last 3 digits
        result = num_str[-3:]
        num_str = num_str[:-3]
        
        # Group remaining digits in 2s
        while len(num_str) > 0:
            if len(num_str) >= 2:
                result = num_str[-2:] + ',' + result
                num_str = num_str[:-2]
            else:
                result = num_str + ',' + result
                num_str = ''
        
        return f"{sign}{result}"
    
    except (ValueError, TypeError):
        return "0"

def extract_lat_lng_from_url(google_maps_url):
    # Parse the URL
    parsed_url = urlparse(google_maps_url)
    # Extract the path and split by '/'
    path_segments = parsed_url.path.split('/')
    for segment in path_segments:
        if '@' in segment:  # Look for the segment with '@' containing coordinates
            coordinates = segment.split('@')[1].split(',')[:2]  # Get lat and lng
            latitude = coordinates[0]
            longitude = coordinates[1]
            return float(latitude), float(longitude)
    return None, None




def save_file(folder_path, uploaded_file, request):
    try:
        # Ensure the folder exists
        os.makedirs(folder_path, exist_ok=True)
        
        # Sanitize the filename
        filename = slugify(Path(uploaded_file.name).stem) + Path(uploaded_file.name).suffix
        file_path = os.path.join(folder_path, filename)

        # Validate MIME type
        mime_type, _ = guess_type(uploaded_file.name)
        if not mime_type:
            return {'msg': 'Invalid file type', 'url': '', 'n': 0}

        # Allowed file types
        allowed_types = ("image/", "video/", "application/pdf", "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        if not any(mime_type.startswith(t) for t in allowed_types):
            return {'msg': 'Unsupported file type.', 'url': '', 'n': 0}

        # Save the uploaded file
        with default_storage.open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

    except Exception as e:
        logging.error(f"Failed to process the file: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        return {'msg': f"Failed to process the file: {e}", 'url': '', 'n': 0}

    # Get the relative file path for the URL
    media_root_path = Path(settings.MEDIA_ROOT).resolve()
    file_path_resolved = Path(file_path).resolve()
    
    try:
        relative_file_path = file_path_resolved.relative_to(media_root_path)
    except ValueError:
        logging.error("File path is outside MEDIA_ROOT. Returning absolute URL.")
        relative_file_path = file_path_resolved  # Fall back to absolute path

    file_url = request.build_absolute_uri(settings.MEDIA_URL + str(relative_file_path).replace("\\", "/"))
    return {'msg': 'File saved successfully', 'url': file_url, 'n': 1}





def send_registration_successful_mail(data):
    email = data.get("email", "").strip().lower()

    # Validate email
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not email or not re.match(email_regex, email):
        return {
            "data": {},
            "response": {"n": 0, "msg": "Invalid or missing email", "status": "error"}
        }

    # ✅ Generate 6-digit OTP (if needed)
    # Uncomment if you plan to send an OTP
    # import random
    # otp = str(random.randint(100000, 999999))
    # data["otp"] = otp

    # Render HTML template with context
    html_content = render_to_string('Mails/registration_successfull_email_template.html', {'data': data})

    # Create email
    subject = "Registration to ERP app was successful"
    body_text = (
        "Congratulations! 🎉\n\n"
        "You have successfully registered for the ERP \n"
        "We’re excited to have you onboard!\n\n"
        "Regards,\nERP Team"
    )

    msg = EmailMultiAlternatives(
        subject=subject,
        body=body_text,
        from_email="no-reply@mozilourislandguide.com",
        to=[email],
    )
    msg.attach_alternative(html_content, "text/html")

    # Send email safely
    try:
        msg.send(fail_silently=False)
        print(f"✅ Registration email sent to {email}")
        return {
            "data": {"email": email},
            "response": {"n": 1, "msg": "Mail sent successfully", "status": "success"}
        }
    except Exception as e:
        print("❌ EMAIL SEND ERROR:", e)
        return {
            "data": {"email": email},
            "response": {"n": 0, "msg": f"Failed to send email: {e}", "status": "error"}
        }
































































