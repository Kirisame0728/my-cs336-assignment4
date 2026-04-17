from cs336_data.quality_classifier.utils import read_jsonl
import argparse
import random

def to_fasttext_line(label: str, text: str) -> str:
    return f"{label} {text}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--positive_jsonl", type=str, required=True)
    parser.add_argument("--negative_jsonl", type=str, required=True)
    parser.add_argument("--train_out", type=str, default="data/train_set/quality_train.txt")
    parser.add_argument("--valid_out", type=str, default="data/train_set/quality_valid.txt")
    parser.add_argument("--valid_ratio", type=float, default=0.1)
    args = parser.parse_args()

    pos = read_jsonl(args.positive_jsonl)
    neg = read_jsonl(args.negative_jsonl)

    all_records = pos + neg
    random.shuffle(all_records)

    split = int(len(all_records) * (1 - args.valid_ratio))
    train_records = all_records[:split]
    valid_records = all_records[split:]

    with open(args.train_out, "w", encoding="utf8") as f:
        for r in train_records:
            f.write(to_fasttext_line(r["label"], r["text"]) + "\n")

    with open(args.valid_out, "w", encoding="utf-8") as f:
        for r in valid_records:
            f.write(to_fasttext_line(r["label"], r["text"]) + "\n")

if __name__ == "__main__":
    main()