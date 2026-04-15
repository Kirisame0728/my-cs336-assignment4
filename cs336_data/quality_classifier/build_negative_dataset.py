import gzip
import argparse
import random
from tqdm import tqdm
import os
import json
from cs336_data.quality_classifier.utils import mask_pii, normalize_text_for_training


def iter_wet_records(wet_gz_path):
    with gzip.open(wet_gz_path, "rt", encoding="utf-8", errors="replace") as f:
        current = []
        for line in f:
            if line.startswith("WARC/1.0"):
                if current:
                    yield "".join(current)
                current = [line]
            else:
                current.append(line)
        if current:
            yield "".join(current)

def parse_wet_record(record):
    lines = record.splitlines()

    url = None
    text_start = None # where texts start at

    for i, line in enumerate(lines):
        if line.startswith("WARC-Target-URI:"):
            url = line[len("WARC-Target-URI:"):].strip()

        if line.strip() == "":
            text_start = i + 1
            break

    if text_start is None:
        return None, None

    text = "\n".join(lines[text_start:]).strip()
    return url, text

def random_sample_negative_records(wet_gz_path, sample_size):
    reservoir = []

    for i, record in enumerate(iter_wet_records(wet_gz_path)):
        url, text = parse_wet_record(record)

        if not text:
            continue
        item = {
            "url": url,
            "text": text,
        }

        if len(reservoir) < sample_size:
            reservoir.append(item)
        else:
            j = random.randint(0, i)
            if j < sample_size:
                reservoir[j] = item
    return reservoir

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wet_gz", type=str, default="data/CC/CC-MAIN-20250417135010-20250417165010-00065.warc.wet.gz")
    parser.add_argument("--num_samples", type=int, default=684)
    parser.add_argument("--output_jsonl", type=str, default="data/samples/negative_samples.jsonl")
    args = parser.parse_args()

    records = random_sample_negative_records(args.wet_gz, args.num_samples)

    cleaned_records = []
    for r in tqdm(records, desc="Cleaning negatives"):
        text = r["text"]
        text = mask_pii(text)
        text = normalize_text_for_training(text)

        if not text:
            continue

        cleaned_records.append(
            {
                "label": "__label__lq",
                "url": r["url"],
                "text": text,
            }
        )

    out_dir = os.path.dirname(args.output_jsonl)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(args.output_jsonl, "w", encoding="utf-8") as f:
        for r in cleaned_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()


