import gzip
import json
import random
import requests
import re
from cs336_data.extract_text import html_to_text



EMAIL_RE = re.compile(
    r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[A-Za-z]{2,}\b"
)

IP_RE = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}"
    r"(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\b"
)

PHONE_RE = re.compile(
    r"""
    (?<!\w)
    (?:\+?1[-.\s]?)?
    (?:\(?\d{3}\)?[-.\s]?)?
    \d{3}[-.\s]?\d{4}
    (?!\w)
    """,
    re.VERBOSE,
)


def iter_gz_lines(path):
    with gzip.open(path, mode="rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line:
                yield line

def random_sample_gz_lines(gz_path, sample_size):
    reservoir = []
    for i, line in enumerate(iter_gz_lines(gz_path)):
        if i < sample_size:
            reservoir.append(line)
        else:
            j = random.randint(0, i)
            if j < sample_size:
                reservoir[j] = line
    return reservoir


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

def normalize_whitespace(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text

def fetch_url_text(url, timeout=8):
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        if resp.status_code != 200:
            return None
        content_type = resp.headers.get("Content-Type", "").lower()
        if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
            return None
        text = html_to_text(resp.content)
        text = normalize_whitespace(text)
        if not text:
            return None
        return text
    except Exception:
        return None


def mask_pii(text: str) -> str:
    text = EMAIL_RE.sub("|||EMAIL_ADDRESS|||", text)
    text = PHONE_RE.sub("|||PHONE_NUMBER|||", text)
    text = IP_RE.sub("|||IP_ADDRESS|||", text)
    return text

def normalize_text_for_training(text: str, max_chars: int = 20000) -> str:
    text = text.lower()
    text = normalize_whitespace(text)
    if len(text) > max_chars:
        text = text[:max_chars]
    return text

def read_jsonl(path):
    records = []
    with open(path, "r", encoding="utf8") as f:
        for line in f:
            records.append(json.loads(line))
    return records