import os
import re
import shutil
from PyPDF2 import PdfMerger

REPO_PATH = "."
STAGING_PATH = "staging"

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
    part = part or "Part1"
    topic_file = f"{topic_file_base}.pdf"

    target_dir = os.path.join(REPO_PATH, domain, subdomain, topic_folder)
    os.makedirs(target_dir, exist_ok=True)

    merged_log = os.path.join(target_dir, f"{topic_file_base}.merged")
    already_merged = []
    if os.path.exists(merged_log):
        with open(merged_log) as f:
            already_merged = [line.strip() for line in f.readlines()]

    if part in already_merged:
        print(f"✅ Skipping {filename} (already merged)")
        return

    target_pdf = os.path.join(target_dir, topic_file)
    new_pdf = os.path.join(STAGING_PATH, filename)

    if os.path.exists(target_pdf):
        merge_pdfs([target_pdf, new_pdf], target_pdf)
    else:
        merge_pdfs([new_pdf], target_pdf)

    with open(merged_log, "a") as f:
        f.write(part + "\n")

    print(f"✅ Merged {filename} → {topic_file}")

def main():
    for pdf in os.listdir(STAGING_PATH):
        if pdf.endswith('.pdf'):
            process_pdf(pdf)

    # ✅ Clear staging for next run
    shutil.rmtree(STAGING_PATH)
    os.makedirs(STAGING_PATH, exist_ok=True)

if __name__ == "__main__":
    main()