import hashlib
import os
from collections import Counter

def hash_line(line):
    return hashlib.blake2b(line.encode("utf-8"), digest_size=16).digest()


def exact_line_deduplication(input_paths, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    line_counts = Counter()

    # Pass 1: count how many occurrences of each line
    for path in input_paths:
        with open(path, "r") as f:
            for line in f:
                line_hash = hash_line(line)
                line_counts[line_hash] += 1

    # Pass 2: Rewrite each document by preserving only its unique lines
    for path in input_paths:
        src_file = os.path.basename(path)
        dst = os.path.join(out_dir, src_file)

        with open(path, "r") as fin, \
                open(dst, "w", encoding="utf-8") as fout:
            for line in fin:
                line_hash = hash_line(line)
                if line_counts[line_hash] == 1:
                    fout.write(line)