import os
import re
import json
import hashlib
from PyPDF2 import PdfMerger

REPO_PATH = "."
STAGING_PATH = "staging"
MERGED_META_DIR = ".merged"

def md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def merge_pdfs(pdfs, output_pdf):
    merger = PdfMerger()
    for pdf in pdfs:
        merger.append(pdf)
    merger.write(output_pdf)
    merger.close()

def process_pdf(filename):
    name, ext = os.path.splitext(filename)
    parts = name.split('-')
    if len(parts) != 4:
        print(f"Invalid filename: {filename}")
        return

    domain, subdomain, topic_folder, topic_file_with_part = parts
    match = re.match(r"(.*?)(Part\d+)?$", topic_file_with_part)
    if not match:
        print(f"Invalid topic file: {topic_file_with_part}")
        return

    topic_file_base, part = match.groups()
    topic_file = f"{topic_file_base}.pdf"

    target_dir = os.path.join(REPO_PATH, domain, subdomain, topic_folder)
    os.makedirs(target_dir, exist_ok=True)

    target_pdf = os.path.join(target_dir, topic_file)
    new_pdf = os.path.join(STAGING_PATH, filename)

    merged_dir = os.path.join(MERGED_META_DIR, domain, subdomain, topic_folder)
    meta_file = os.path.join(merged_dir, f"{topic_file_base}.json")

    new_md5 = md5(new_pdf)

    if os.path.exists(meta_file):
        with open(meta_file, 'r') as f:
            merged_parts = json.load(f)
    else:
        merged_parts = []

    if new_md5 in merged_parts:
        print(f"✅ Already merged: {filename} — skip")
        return

    if os.path.exists(target_pdf):
        merge_pdfs([target_pdf, new_pdf], target_pdf)
    else:
        merge_pdfs([new_pdf], target_pdf)

    # ✅ Only now: ensure .merged/ path exists
    os.makedirs(merged_dir, exist_ok=True)

    # Save the new hash to JSON
    merged_parts.append(new_md5)
    with open(meta_file, 'w') as f:
        json.dump(merged_parts, f)
    print(f"✅ Merged: {filename}")

def main():
    if not os.path.exists(STAGING_PATH) or not os.listdir(STAGING_PATH):
        print("✅ Nothing to process — staging is empty.")
        return

    for pdf in os.listdir(STAGING_PATH):
        if pdf.endswith('.pdf'):
            process_pdf(pdf)

if __name__ == "__main__":
    main()