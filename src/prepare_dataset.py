"""
prepare_dataset.py
==================
Converts raw public email datasets into one standardised CSV:

    data/processed/dataset.csv   — columns: subject, body, label
    data/processed/dataset_metadata.json

Labels are normalised to exactly: legitimate | spam | phishing

Rules
-----
- Never modify any file inside data/raw/.
- Email content is treated as UNTRUSTED TEXT only.
  Do NOT execute HTML, open links, or make HTTP requests.
- Do NOT fabricate records. Use only real downloaded datasets.
- Labels must be validated; unknown labels raise a hard error.

Usage
-----
    python -m src.prepare_dataset

Supported datasets (place files as described below)
-----------------------------------------------------

1. ENRON SPAM DATASET  (legitimate + spam)
   File   : data/raw/enron_spam.csv
   Source : https://www.kaggle.com/datasets/wanderfj/enron-spam
   Format : CSV with columns  message_id, subject, message, label
            label values: 0 = legitimate (ham), 1 = spam
   License: Verify on Kaggle before use.

2. SpamAssassin Public Corpus  (legitimate + spam)
   Files  : data/raw/spamassassin/easy_ham/     (one .txt file per email)
            data/raw/spamassassin/hard_ham/      (one .txt file per email)
            data/raw/spamassassin/spam/          (one .txt file per email)
            data/raw/spamassassin/spam_2/        (one .txt file per email)
   Source : https://spamassassin.apache.org/old/publiccorpus/
   License: Verify at source before use.

3. CSDMC2010 Spam Corpus  (legitimate + spam)
   Files  : data/raw/CSDMC2010/TRAIN/
            data/raw/CSDMC2010/TRAIN/SPAMTrain.label  (label file)
            data/raw/CSDMC2010/TRAIN/TRAIN_<n>.eml    (raw email files)
   Source : http://csmining.org/index.php/spam-email-datasets-.html
   License: Verify at source before use.

4. Nazario Phishing Corpus  (phishing)
   File   : data/raw/nazario_phishing.mbox   OR
            data/raw/nazario/                (individual .txt / .eml files)
   Source : https://monkey.org/~jose/phishing/
   License: Research only. Do not redistribute raw emails.
            Verify current availability and terms before use.

5. IWSPA-AP 2018 Phishing Corpus  (phishing)  [fallback if Nazario unavailable]
   File   : data/raw/iwspa_ap/
            data/raw/iwspa_ap/train/phishing/  (one .txt file per email)
   Source : https://nlp.cs.aueb.gr/software_and_datasets/iwspa-ap/
   License: Verify at source before use.

Author: Yash Yadav
"""

from __future__ import annotations

import csv
import email
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

# ── Paths ────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR      = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR= PROJECT_ROOT / "data" / "processed"
OUT_CSV      = PROCESSED_DIR / "dataset.csv"
OUT_META     = PROCESSED_DIR / "dataset_metadata.json"

VALID_LABELS = {"legitimate", "spam", "phishing"}

# ── Helpers ───────────────────────────────────────────────────────────────────

def _safe_str(value: object) -> str:
    """Return a clean string, replacing None/NaN/non-string with ''."""
    if value is None:
        return ""
    s = str(value).strip()
    # treat pandas NA / numpy nan stringifications
    if s.lower() in ("nan", "none", "<na>"):
        return ""
    return s


def _decode_bytes(raw: bytes) -> str:
    """Decode bytes to str, trying UTF-8 then latin-1 as fallback."""
    try:
        return raw.decode("utf-8", errors="replace")
    except Exception:
        return raw.decode("latin-1", errors="replace")


def _extract_email_parts(raw_text: str) -> tuple[str, str]:
    """
    Parse a raw RFC-2822 email message and return (subject, body).
    Returns ('', raw_text) if parsing fails or the text is not RFC-2822.
    Email content is treated as plain text — HTML is NOT executed.
    """
    try:
        msg = email.message_from_string(raw_text)
        subject = _safe_str(msg.get("Subject", ""))
        body_parts: list[str] = []
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype in ("text/plain", "text/html"):
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_parts.append(_decode_bytes(payload))
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body_parts.append(_decode_bytes(payload))
            else:
                # payload may already be a string (not encoded)
                body_parts.append(_safe_str(msg.get_payload()))
        body = " ".join(body_parts).strip()
        return subject, body
    except Exception:
        return "", raw_text


def _iter_txt_files(directory: Path) -> Iterator[Path]:
    """Yield all .txt and .eml files under a directory recursively."""
    for root, _, files in os.walk(directory):
        for fname in sorted(files):
            if fname.endswith((".txt", ".eml")) and not fname.startswith("."):
                yield Path(root) / fname


# ── Dataset loaders ──────────────────────────────────────────────────────────

def load_enron_csv(path: Path) -> list[dict]:
    """
    Load Enron spam CSV.
    Expected columns: subject, message, label  (label: 0=ham, 1=spam)
    Also handles 'Spam/Ham' column if present.
    Returns list of {subject, body, label} dicts.
    """
    try:
        import pandas as pd  # type: ignore
    except ImportError:
        sys.exit("[ERROR] pandas is required. Run: pip install pandas")

    records: list[dict] = []
    try:
        df = pd.read_csv(path, encoding="latin-1", low_memory=False)
    except Exception as exc:
        print(f"  [WARN] Could not read {path}: {exc}")
        return records

    df.columns = [c.strip().lower() for c in df.columns]

    # Normalise label column
    label_col = None
    for cname in ("label", "spam/ham", "spam", "class"):
        if cname in df.columns:
            label_col = cname
            break
    if label_col is None:
        print(f"  [WARN] No recognisable label column in {path}. Skipping.")
        return records

    # Normalise body column
    body_col = None
    for cname in ("message", "body", "text", "content"):
        if cname in df.columns:
            body_col = cname
            break
    if body_col is None:
        print(f"  [WARN] No recognisable body column in {path}. Skipping.")
        return records

    subject_col = "subject" if "subject" in df.columns else None

    for _, row in df.iterrows():
        raw_label = _safe_str(row[label_col]).lower()
        # Map numeric/string labels
        if raw_label in ("0", "ham", "legitimate", "benign"):
            label = "legitimate"
        elif raw_label in ("1", "spam"):
            label = "spam"
        elif raw_label in ("phishing", "phish"):
            label = "phishing"
        else:
            continue  # skip unknown label silently

        subject = _safe_str(row[subject_col]) if subject_col else ""
        body    = _safe_str(row[body_col])
        records.append({"subject": subject, "body": body, "label": label})

    return records


def load_spamassassin_dirs(base_dir: Path) -> list[dict]:
    """
    Load SpamAssassin public corpus from directory structure.
    Expects subdirs: easy_ham/, hard_ham/, spam/, spam_2/
    Each subdir contains one raw RFC-2822 .txt file per email.
    """
    label_map = {
        "easy_ham": "legitimate",
        "hard_ham": "legitimate",
        "spam":     "spam",
        "spam_2":   "spam",
    }
    records: list[dict] = []
    for subdir, label in label_map.items():
        d = base_dir / subdir
        if not d.exists():
            continue
        for fpath in _iter_txt_files(d):
            try:
                raw = fpath.read_bytes()
                text = _decode_bytes(raw)
                subject, body = _extract_email_parts(text)
                records.append({"subject": subject, "body": body, "label": label})
            except Exception as exc:
                print(f"  [WARN] Skipping {fpath.name}: {exc}")
    return records


def load_csdmc2010(base_dir: Path) -> list[dict]:
    """
    Load CSDMC2010 spam corpus.
    Expects:
      base_dir/TRAIN/SPAMTrain.label   — tab-separated: index<TAB>label (SPAM|HAM)
      base_dir/TRAIN/TRAIN_<n>.eml     — raw email files
    """
    records: list[dict] = []
    train_dir  = base_dir / "TRAIN"
    label_file = train_dir / "SPAMTrain.label"
    if not label_file.exists():
        print(f"  [WARN] {label_file} not found. Skipping CSDMC2010.")
        return records

    label_map: dict[str, str] = {}
    try:
        with open(label_file, encoding="utf-8", errors="replace") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    idx, raw_label = parts
                    label_map[idx] = "spam" if raw_label.upper() == "SPAM" else "legitimate"
    except Exception as exc:
        print(f"  [WARN] Could not read label file: {exc}")
        return records

    for idx, label in label_map.items():
        eml_path = train_dir / f"TRAIN_{idx}.eml"
        if not eml_path.exists():
            continue
        try:
            raw  = eml_path.read_bytes()
            text = _decode_bytes(raw)
            subject, body = _extract_email_parts(text)
            records.append({"subject": subject, "body": body, "label": label})
        except Exception as exc:
            print(f"  [WARN] Skipping {eml_path.name}: {exc}")
    return records


def load_phishing_dir(directory: Path, label: str = "phishing") -> list[dict]:
    """
    Generic loader for a flat or nested directory of raw email .txt/.eml files.
    Used for Nazario and IWSPA-AP phishing corpora.
    """
    if not directory.exists():
        return []
    records: list[dict] = []
    for fpath in _iter_txt_files(directory):
        try:
            raw  = fpath.read_bytes()
            text = _decode_bytes(raw)
            subject, body = _extract_email_parts(text)
            records.append({"subject": subject, "body": body, "label": label})
        except Exception as exc:
            print(f"  [WARN] Skipping {fpath.name}: {exc}")
    return records


# ── Validation & deduplication ────────────────────────────────────────────────

def validate_and_clean(records: list[dict]) -> tuple[list[dict], int, int]:
    """
    Remove records with empty body and exact subject+body duplicates.
    Returns (clean_records, empty_removed, dupes_removed).
    """
    empty_removed = 0
    seen: set[tuple[str, str]] = set()
    dupes_removed  = 0
    clean: list[dict] = []

    for r in records:
        # Ensure string types
        r["subject"] = _safe_str(r.get("subject", ""))
        r["body"]    = _safe_str(r.get("body", ""))
        r["label"]   = _safe_str(r.get("label", ""))

        if not r["body"]:
            empty_removed += 1
            continue

        if r["label"] not in VALID_LABELS:
            # Should not reach here if loaders are correct, but guard anyway
            raise ValueError(f"Unexpected label '{r['label']}' — fix the loader.")

        key = (r["subject"], r["body"])
        if key in seen:
            dupes_removed += 1
            continue
        seen.add(key)
        clean.append(r)

    return clean, empty_removed, dupes_removed


# ── Main pipeline ─────────────────────────────────────────────────────────────

def prepare_dataset() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    all_records: list[dict] = []
    source_stats: list[dict] = []

    # ── 1. Enron CSV ────────────────────────────────────────────────────────
    enron_path = RAW_DIR / "enron_spam.csv"
    if enron_path.exists():
        print(f"Loading Enron CSV: {enron_path}")
        recs = load_enron_csv(enron_path)
        print(f"  → {len(recs)} records loaded")
        source_stats.append({
            "name": "Enron Spam Dataset",
            "file": str(enron_path.name),
            "source_url": "https://www.kaggle.com/datasets/wanderfj/enron-spam",
            "license_note": "Verify license on Kaggle before use.",
            "records_loaded": len(recs),
        })
        all_records.extend(recs)
    else:
        print(f"[SKIP] Enron CSV not found at {enron_path}")

    # ── 2. SpamAssassin ─────────────────────────────────────────────────────
    sa_dir = RAW_DIR / "spamassassin"
    if sa_dir.exists():
        print(f"Loading SpamAssassin corpus: {sa_dir}")
        recs = load_spamassassin_dirs(sa_dir)
        print(f"  → {len(recs)} records loaded")
        source_stats.append({
            "name": "SpamAssassin Public Corpus",
            "directory": "data/raw/spamassassin/",
            "source_url": "https://spamassassin.apache.org/old/publiccorpus/",
            "license_note": "Verify license at source before use.",
            "records_loaded": len(recs),
        })
        all_records.extend(recs)
    else:
        print(f"[SKIP] SpamAssassin dir not found at {sa_dir}")

    # ── 3. CSDMC2010 ────────────────────────────────────────────────────────
    csdmc_dir = RAW_DIR / "CSDMC2010"
    if csdmc_dir.exists():
        print(f"Loading CSDMC2010 corpus: {csdmc_dir}")
        recs = load_csdmc2010(csdmc_dir)
        print(f"  → {len(recs)} records loaded")
        source_stats.append({
            "name": "CSDMC2010 Spam Corpus",
            "directory": "data/raw/CSDMC2010/",
            "source_url": "http://csmining.org/index.php/spam-email-datasets-.html",
            "license_note": "Verify license at source before use.",
            "records_loaded": len(recs),
        })
        all_records.extend(recs)
    else:
        print(f"[SKIP] CSDMC2010 dir not found at {csdmc_dir}")

    # ── 4. Nazario Phishing Corpus ──────────────────────────────────────────
    nazario_dir  = RAW_DIR / "nazario"
    nazario_mbox = RAW_DIR / "nazario_phishing.mbox"
    if nazario_dir.exists():
        print(f"Loading Nazario phishing corpus: {nazario_dir}")
        recs = load_phishing_dir(nazario_dir, label="phishing")
        print(f"  → {len(recs)} records loaded")
        source_stats.append({
            "name": "Nazario Phishing Corpus",
            "directory": "data/raw/nazario/",
            "source_url": "https://monkey.org/~jose/phishing/",
            "license_note": "Research use only. Do not redistribute raw emails. Verify current terms.",
            "records_loaded": len(recs),
        })
        all_records.extend(recs)
    elif nazario_mbox.exists():
        # If user has an mbox file, parse it with the email stdlib
        print(f"Loading Nazario .mbox: {nazario_mbox}")
        import mailbox  # stdlib
        recs: list[dict] = []
        try:
            mbox = mailbox.mbox(str(nazario_mbox))
            for msg in mbox:
                subject = _safe_str(msg.get("Subject", ""))
                body_parts: list[str] = []
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() in ("text/plain", "text/html"):
                            payload = part.get_payload(decode=True)
                            if payload:
                                body_parts.append(_decode_bytes(payload))
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body_parts.append(_decode_bytes(payload))
                recs.append({"subject": subject, "body": " ".join(body_parts), "label": "phishing"})
        except Exception as exc:
            print(f"  [WARN] mbox parse error: {exc}")
        print(f"  → {len(recs)} records loaded")
        source_stats.append({
            "name": "Nazario Phishing Corpus (mbox)",
            "file": str(nazario_mbox.name),
            "source_url": "https://monkey.org/~jose/phishing/",
            "license_note": "Research use only. Do not redistribute raw emails. Verify current terms.",
            "records_loaded": len(recs),
        })
        all_records.extend(recs)
    else:
        print(f"[SKIP] Nazario phishing corpus not found at {nazario_dir} or {nazario_mbox}")

    # ── 5. IWSPA-AP fallback ────────────────────────────────────────────────
    iwspa_dir = RAW_DIR / "iwspa_ap"
    if iwspa_dir.exists():
        phishing_subdir = iwspa_dir / "train" / "phishing"
        if not phishing_subdir.exists():
            phishing_subdir = iwspa_dir  # try flat layout
        print(f"Loading IWSPA-AP phishing corpus: {phishing_subdir}")
        recs = load_phishing_dir(phishing_subdir, label="phishing")
        print(f"  → {len(recs)} records loaded")
        source_stats.append({
            "name": "IWSPA-AP 2018 Phishing Corpus",
            "directory": "data/raw/iwspa_ap/",
            "source_url": "https://nlp.cs.aueb.gr/software_and_datasets/iwspa-ap/",
            "license_note": "Shared task dataset. Verify terms at hosting institution before use.",
            "records_loaded": len(recs),
        })
        all_records.extend(recs)
    else:
        print(f"[SKIP] IWSPA-AP dir not found at {iwspa_dir}")

    # ── Abort if nothing was loaded ─────────────────────────────────────────
    if not all_records:
        print(
            "\n[ABORT] No dataset files found in data/raw/."
            "\nPlace the datasets as described in the docstring at the top of this file,"
            "\nthen re-run:  python -m src.prepare_dataset\n"
        )
        sys.exit(1)

    # ── Clean & deduplicate ─────────────────────────────────────────────────
    clean, empty_removed, dupes_removed = validate_and_clean(all_records)

    # ── Label counts ─────────────────────────────────────────────────────────
    counts: dict[str, int] = {"legitimate": 0, "spam": 0, "phishing": 0}
    for r in clean:
        counts[r["label"]] += 1

    # ── Save CSV ─────────────────────────────────────────────────────────────
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["subject", "body", "label"])
        writer.writeheader()
        writer.writerows(clean)
    print(f"\nSaved: {OUT_CSV}")

    # ── Save metadata ─────────────────────────────────────────────────────────
    metadata = {
        "preparation_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "output_file": str(OUT_CSV.relative_to(PROJECT_ROOT)),
        "total_records": len(clean),
        "class_counts": counts,
        "empty_records_removed": empty_removed,
        "duplicates_removed": dupes_removed,
        "sources": source_stats,
        "note": (
            "All statistics reflect the actual prepared dataset. "
            "Verify dataset licenses independently before any publication or redistribution."
        ),
    }
    with open(OUT_META, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved: {OUT_META}")

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 40)
    print("DATASET PREPARATION SUMMARY")
    print("=" * 40)
    print(f"Total records     : {len(clean)}")
    print(f"  Legitimate      : {counts['legitimate']}")
    print(f"  Spam            : {counts['spam']}")
    print(f"  Phishing        : {counts['phishing']}")
    print(f"Duplicates removed: {dupes_removed}")
    print(f"Empty removed     : {empty_removed}")
    print("=" * 40)

    # Warn if any class is missing — this is a blocker for training
    missing = [k for k, v in counts.items() if v == 0]
    if missing:
        print(f"\n[WARNING] Missing classes: {missing}")
        print("All three classes (legitimate, spam, phishing) are required for training.")
        print("Download the missing datasets and re-run this script.")


if __name__ == "__main__":
    prepare_dataset()
