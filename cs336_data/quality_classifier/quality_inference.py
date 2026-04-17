import re
import fasttext

_MODEL = None

def get_model(model_path="data/quality_classifier.bin"):
    global _MODEL
    if _MODEL is None:
        _MODEL = fasttext.load_model(model_path)
    return _MODEL

def normalize_text(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text

def classify_quality(text, threshold=0.0, model_path="data/quality_classifier.bin"):
    text = normalize_text(text)
    model = get_model(model_path)

    labels, scores = model.predict(text, k=2)

    probs = {label: float(score) for label, score in zip(labels, scores)}
    hq_score = probs.get("__label__hq", 0.0)

    if hq_score >= threshold:
        return ("wiki", hq_score)
    else:
        return ("cc", hq_score)
