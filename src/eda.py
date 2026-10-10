"""
eda.py
======
Exploratory Data Analysis for the email spam/phishing dataset.

Usage
-----
    python -m src.eda

Saves figures to reports/figures/.
All statistics are computed from the actual dataset.
"""

from __future__ import annotations

import sys
from pathlib import Path
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURES_DIR  = PROJECT_ROOT / "reports" / "figures"
DATASET_CSV  = PROJECT_ROOT / "data" / "processed" / "dataset.csv"


def run_eda() -> None:
    if not DATASET_CSV.exists():
        sys.exit(f"[ERROR] {DATASET_CSV} not found. Run: python -m src.prepare_dataset")

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATASET_CSV, encoding="utf-8")
    df["subject"] = df["subject"].fillna("").astype(str)
    df["body"]    = df["body"].fillna("").astype(str)

    print("=" * 50)
    print("DATASET EDA SUMMARY")
    print("=" * 50)
    print(f"Total records     : {len(df)}")
    print(f"Missing subjects  : {(df['subject'] == '').sum()}")
    print(f"Missing bodies    : {(df['body'] == '').sum()}")
    print()
    counts = df["label"].value_counts()
    print("Class distribution:")
    for lbl, cnt in counts.items():
        pct = 100 * cnt / len(df)
        print(f"  {lbl:12s}: {cnt:6d}  ({pct:.1f}%)")

    df["body_len"]    = df["body"].str.len()
    df["body_words"]  = df["body"].str.split().str.len()
    df["subject_len"] = df["subject"].str.len()

    print()
    print("Body length statistics (chars):")
    print(df.groupby("label")["body_len"].describe()[["mean", "50%", "max"]].round(0))
    print()
    print("Body word count statistics:")
    print(df.groupby("label")["body_words"].describe()[["mean", "50%", "max"]].round(0))

    # ── Figure 1: class distribution bar chart ────────────────────────────────
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = {"legitimate": "steelblue", "spam": "darkorange", "phishing": "firebrick"}
    bars = ax.bar(counts.index, counts.values,
                  color=[colors.get(l, "gray") for l in counts.index])
    ax.set_title("Class Distribution")
    ax.set_xlabel("Class")
    ax.set_ylabel("Count")
    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                str(val), ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "class_distribution.png", dpi=150)
    plt.close()
    print("\nSaved: class_distribution.png")

    # ── Figure 2: body length distribution ────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 4))
    for lbl, color in colors.items():
        subset = df[df["label"] == lbl]["body_len"]
        if len(subset):
            ax.hist(subset.clip(upper=10_000), bins=50, alpha=0.6, label=lbl, color=color)
    ax.set_title("Body Length Distribution (chars, capped at 10k)")
    ax.set_xlabel("Length")
    ax.set_ylabel("Frequency")
    ax.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "body_length_distribution.png", dpi=150)
    plt.close()
    print("Saved: body_length_distribution.png")

    # ── Figure 3: subject length distribution ─────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 4))
    for lbl, color in colors.items():
        subset = df[df["label"] == lbl]["subject_len"]
        if len(subset):
            ax.hist(subset.clip(upper=200), bins=40, alpha=0.6, label=lbl, color=color)
    ax.set_title("Subject Length Distribution (chars, capped at 200)")
    ax.set_xlabel("Length")
    ax.set_ylabel("Frequency")
    ax.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "subject_length_distribution.png", dpi=150)
    plt.close()
    print("Saved: subject_length_distribution.png")

    # ── Figure 4: top-10 words by class (simple) ──────────────────────────────
    STOP = {
        "the", "a", "an", "and", "or", "to", "of", "in", "is", "it",
        "for", "on", "with", "this", "that", "be", "at", "from", "as",
        "i", "you", "your", "we", "our", "have", "are", "was", "will",
        "not", "s", "t", "re", "ll", "ve", "d", "m",
    }
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, (lbl, color) in zip(axes, colors.items()):
        subset = df[df["label"] == lbl]["body"]
        if subset.empty:
            ax.set_title(lbl)
            continue
        words: Counter = Counter()
        for text in subset.head(5000):  # cap for speed
            for w in text.lower().split():
                if w.isalpha() and w not in STOP and len(w) > 2:
                    words[w] += 1
        top = words.most_common(10)
        if top:
            terms, freqs = zip(*top)
            ax.barh(list(reversed(terms)), list(reversed(freqs)), color=color)
            ax.set_title(f"Top Words — {lbl}")
            ax.set_xlabel("Count")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "top_words_by_class.png", dpi=150)
    plt.close()
    print("Saved: top_words_by_class.png")
    print("\nEDA complete.")


if __name__ == "__main__":
    run_eda()
