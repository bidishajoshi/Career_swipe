import sys
import os

# Add utils to path
sys.path.insert(0, r"c:\Users\VICTUS\Desktop\career-swipe")

from utils.resume_parser import convert_docx_to_pdf

docx_path = r"c:\Users\VICTUS\Desktop\career-swipe\static\uploads\resumes\439387f8-cb8d-41ea-b5d4-c5d41e2af0d7_CORBA_Sample_Program.docx"
output_folder = r"c:\Users\VICTUS\Desktop\career-swipe\static\uploads\resumes"

print(f"Converting: {docx_path}")
print(f"Output folder: {output_folder}")

if os.path.exists(docx_path):
    pdf_path = convert_docx_to_pdf(docx_path, output_folder)
    if pdf_path and os.path.exists(pdf_path):
        print(f"✓ Successfully converted to: {pdf_path}")
    else:
        print("✗ Conversion failed")
else:
    print("✗ File not found")
