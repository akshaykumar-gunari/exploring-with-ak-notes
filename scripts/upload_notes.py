import os
import re
import shutil
from PyPDF2 import PdfMerger

REPO_PATH = "."
STAGING_PATH = "staging"
MERGED_PATH = ".merged"

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
        print(f"❌ Invalid filename: {filename}")
        return

    domain, subdomain, topic_folder, topic_file_with_part = parts

    match = re.match(r"(.*?)(Part\d+)?$", topic_file_with_part)
    if not match:
        print(f"❌ Invalid topic file: {topic_file_with_part}")
        return

    topic_file_base, part = match.groups()
    topic_file = f"{topic_file_base}.pdf"

    target_dir = os.path.join(REPO_PATH, domain, subdomain, topic_folder)
    os.makedirs(target_dir, exist_ok=True)
    os.makedirs(MERGED_PATH, exist_ok=True)

    target_pdf = os.path.join(target_dir, topic_file)
    staged_pdf = os.path.join(STAGING_PATH, filename)

    # Merged version to check for changes
    merged_marker = os.path.join(MERGED_PATH, topic_file)

    # If the final PDF does not exist yet:
    if not os.path.exists(target_pdf):
        print(f"🆕 Creating new: {target_pdf}")
        merge_pdfs([staged_pdf], target_pdf)
        shutil.copy2(target_pdf, merged_marker)
    else:
        # Compare with merged marker to detect real change
        if not os.path.exists(merged_marker):
            shutil.copy2(target_pdf, merged_marker)

        print(f"🔍 Checking for new content...")
        temp_merged = f"{merged_marker}.tmp.pdf"
        merge_pdfs([merged_marker, staged_pdf], temp_merged)

        if open(temp_merged, 'rb').read() == open(merged_marker, 'rb').read():
            print(f"✅ No new changes. Skipping: {filename}")
            os.remove(temp_merged)
        else:
            print(f"✅ Appending new content to: {target_pdf}")
            shutil.copy2(temp_merged, target_pdf)
            shutil.copy2(temp_merged, merged_marker)
            os.remove(temp_merged)

    # Clean up staged file
    os.remove(staged_pdf)
    print(f"🗑️ Removed staged: {filename}")

def main():
    for pdf in os.listdir(STAGING_PATH):
        if pdf.endswith('.pdf'):
            process_pdf(pdf)

if __name__ == "__main__":
    main()