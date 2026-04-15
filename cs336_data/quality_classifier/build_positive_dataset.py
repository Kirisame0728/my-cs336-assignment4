import argparse
import json
from tqdm import tqdm
import os
from cs336_data.language_identification import identify_lang
from cs336_data.harmful_content import classify_nsfw, classify_toxic_speech
from cs336_data.gopher_quality_filters import run_gopher_rules
from utils import random_sample_gz_lines
from utils import fetch_url_text
from utils import mask_pii
from utils import normalize_text_for_training


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wiki_urls_gz", type=str, required=True)
    parser.add_argument("--num_urls", type=int, default=2000)
    parser.add_argument("--output_jsonl", type=str, default="data/samples/positive_samples.jsonl")
    args = parser.parse_args()

    urls = random_sample_gz_lines(args.wiki_urls_gz, args.num_urls)

    records = []
    kept = 0

    for i, url in enumerate(tqdm(urls,desc="Fetching positives"), 1):
        text = fetch_url_text(url)
        if not text:
            continue
        label, _ = identify_lang(text)
        if label != "en":
            continue
        nsfw, _ = classify_nsfw(text)
        toxic, _ = classify_toxic_speech(text)
        if nsfw != "non-nsfw" or toxic != "non-toxic":
            continue
        if not run_gopher_rules(text):
            continue
        text = mask_pii(text)
        text = normalize_text_for_training(text)

        if not text:
            continue

        records.append(
            {
                "label": "__label__hq",
                "url": url,
                "text": text,
            }
        )
        kept += 1

        if i % 100 == 0:
            print(f"[positive] processed={i}, kept={kept}")
    out_dir = os.path.dirname(args.output_jsonl)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.output_jsonl, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Saved {len(records)} positive samples to {args.output_jsonl}")


if __name__ == "__main__":
    main()