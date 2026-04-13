from resiliparse.extract.html2text import extract_plain_text
from resiliparse.parse.encoding import detect_encoding

def html_to_text(html_bytes):
    try:
        html_str = html_bytes.decode("utf-8")
    except UnicodeDecodeError:
        enc = detect_encoding(html_bytes)
        html_str = html_bytes.decode(enc)

    text = extract_plain_text(html_str)
    return text
