import os
import re
import json
import hashlib
from PyPDF2 import PdfMerger

REPO_PATH = "."
STAGING_PATH = "staging"
MERGED_META = ".merged"

def md5sum(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def merge_pdfs(pdf_list, output_pdf):
    merger = PdfMerger()
    for pdf in pdf_list:
        merger.append(pdf)
    merger.write(output_pdf)
    merger.close()

def process_pdf(filename):
    name, ext = os.path.splitext(filename)
    parts = name.split('-')
    if len(parts) < 4:
        print(f"Invalid filename: {filename}")
        return

    domain = parts[0]
    subdomain = parts[1]
    topic_folder = parts[2]
    topic_file_with_part = '-'.join(parts[3:])  # join rest

    print(f"DEBUG: domain={domain}, subdomain={subdomain}, topic_folder={topic_folder}, topic_file_with_part={topic_file_with_part}")

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

    os.makedirs(MERGED_META, exist_ok=True)

    new_hash = md5sum(new_pdf)

    if os.path.exists(meta_file):
        with open(meta_file) as f:
            meta = json.load(f)
    else:
        meta = {"merged_hashes": []}

    if new_hash in meta["merged_hashes"]:
        print(f"Already merged: {filename}")
        return

    if os.path.exists(target_pdf):
        merge_pdfs([target_pdf, new_pdf], target_pdf)
    else:
        merge_pdfs([new_pdf], target_pdf)

    meta["merged_hashes"].append(new_hash)
    with open(meta_file, 'w') as f:
        json.dump(meta, f, indent=2)

    print(f"Merged: {filename}")

def main():
    for pdf in os.listdir(STAGING_PATH):
        if pdf.endswith('.pdf'):
            process_pdf(pdf)

if __name__ == "__main__":
    main()