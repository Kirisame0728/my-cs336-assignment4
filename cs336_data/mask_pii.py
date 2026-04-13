import re

def mask_email(text):
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    new_text, count = re.subn(email_pattern, "|||EMAIL_ADDRESS|||", text)
    return new_text, count

def mask_phone(text):
    phone_pattern = r"(?<!\w)(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}(?!\w)"
    new_text, count = re.subn(phone_pattern, "|||PHONE_NUMBER|||", text)
    return new_text, count

def mask_ip(text):
    ip_pattern = r"\b(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}\b"
    new_text, count = re.subn(ip_pattern, "|||IP_ADDRESS|||", text)
    return new_text, count