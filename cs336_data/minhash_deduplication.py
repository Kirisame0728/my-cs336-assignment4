from __future__ import annotations

import os
import re
import math
import random
import hashlib
import unicodedata
from pathlib import Path
from collections import defaultdict
from itertools import combinations
from typing import List, Tuple


_PUNCT_RE = re.compile(r"[^\w\s]", flags=re.UNICODE)
_WS_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = text.lower()

    # remove accents: drop combining marks after NFD
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")

    # remove punctuation
    text = _PUNCT_RE.sub(" ", text)

    # normalize whitespace
    text = _WS_RE.sub(" ", text).strip()
    return text

def get_word_ngrams(text: str, n: int) -> set[str]:
    words = text.split()
    if len(words) < n:
        return set()

    return {
        " ".join(words[i:i+n])
        for i in range(len(words) - n + 1)
    }

def stable_hash_64(text: str, seed: int) -> int:
    h = hashlib.blake2b(digest_size=8)
    h.update(seed.to_bytes(8, byteorder="little", signed=False))
    h.update(text.encode("utf-8"))
    return int.from_bytes(h.digest(), byteorder="little", signed=False)


def compute_minhash_signature(ngrams: set[str], num_hashes: int) -> List[int]:
    if not ngrams:
        # handle empty-doc case deterministically
        return [2**64 - 1] * num_hashes

    signature = []
    for seed in range(num_hashes):
        min_val = min(stable_hash_64(ngram, seed) for ngram in ngrams)
        signature.append(min_val)
    return signature

def jaccard_similarity(set1: set[str], set2: set[str]) -> float:
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    inter = len(set1 & set2)
    union = len(set1 | set2)
    return inter / union

class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra = self.find(a)
        rb = self.find(b)
        if ra == rb:
            return

        if self.rank[ra] < self.rank[rb]:
            self.parent[ra] = rb
        elif self.rank[ra] > self.rank[rb]:
            self.parent[rb] = ra
        else:
            self.parent[rb] = ra
            self.rank[ra] += 1


def minhash_deduplication(input_paths, num_hashes, num_bands, ngram_size, output_dir, jaccard_threshold=0.8, random_seed=42):
    os.makedirs(output_dir, exist_ok=True)
    rows_per_band = num_hashes // num_bands

    # Step 1: read docs, normalize, get ngrams, signatures
    docs_raw: List[str] = []
    docs_norm: List[str] = []
    docs_ngrams: List[set[str]] = []
    signatures: List[List[int]] = []

    for path in input_paths:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        norm_text = normalize_text(text)
        ngrams = get_word_ngrams(norm_text, ngram_size)
        sig = compute_minhash_signature(ngrams, num_hashes)

        docs_raw.append(text)
        docs_norm.append(norm_text)
        docs_ngrams.append(ngrams)
        signatures.append(sig)

    # Step 2: LSH bucketization to find candidate pairs
    candidate_pairs = set()

    for band_idx in range(num_bands):
        start = band_idx * rows_per_band
        end = start + rows_per_band

        buckets: defaultdict[Tuple[int, ...], List[int]] = defaultdict(list)

        for doc_id, sig in enumerate(signatures):
            band = tuple(sig[start:end])
            buckets[band].append(doc_id)

        # docs in the same bucket are candidate duplicates
        for doc_ids in buckets.values():
            if len(doc_ids) < 2:
                continue
            for i, j in combinations(doc_ids, 2):
                if i < j:
                    candidate_pairs.add((i, j))
                else:
                    candidate_pairs.add((j, i))

    # Step 3: verify candidate pairs using true Jaccard
    uf = UnionFind(len(input_paths))

    for i, j in candidate_pairs:
        sim = jaccard_similarity(docs_ngrams[i], docs_ngrams[j])
        if sim >= jaccard_threshold:
            uf.union(i, j)

    # Step 4: build duplicate clusters
    clusters: defaultdict[int, List[int]] = defaultdict(list)
    for doc_id in range(len(input_paths)):
        root = uf.find(doc_id)
        clusters[root].append(doc_id)

    # Step 5: keep one random doc per cluster
    rng = random.Random(random_seed)
    keep_doc_ids = set()

    for cluster_doc_ids in clusters.values():
        chosen = rng.choice(cluster_doc_ids)
        keep_doc_ids.add(chosen)

    # Step 6: write kept docs to output_dir with same filename
    for doc_id, input_path in enumerate(input_paths):
        if doc_id not in keep_doc_ids:
            continue

        src = Path(input_path)
        dst = Path(output_dir) / src.name

        with open(dst, "w", encoding="utf-8") as f:
            f.write(docs_raw[doc_id])


