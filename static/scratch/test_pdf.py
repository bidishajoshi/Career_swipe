import pdfplumber
import os

path = r"c:\Users\VICTUS\Desktop\career-swipe\static\uploads\resumes\8f01b22b-18b6-4ef4-bff0-74ff3923d7ae_beni_kumal_docs_in_pdf_new.pdf"

print(f"Testing file: {path}")
if not os.path.exists(path):
    print("File not found.")
else:
    try:
        with pdfplumber.open(path) as pdf:
            print(f"Number of pages: {len(pdf.pages)}")
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                print(f"Page {i+1} text length: {len(text) if text else 0}")
                if text:
                   print(f"Snippet: {text[:100]}...")
    except Exception as e:
        print(f"Error: {e}")
