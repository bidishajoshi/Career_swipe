from docx import Document
import os

path = r"c:\Users\VICTUS\Desktop\career-swipe\static\uploads\resumes\439387f8-cb8d-41ea-b5d4-c5d41e2af0d7_CORBA_Sample_Program.docx"

print(f"Testing file: {path}")
if not os.path.exists(path):
    print("File not found.")
else:
    try:
        doc = Document(path)
        text = "\n".join([para.text for para in doc.paragraphs])
        print(f"Text length: {len(text)}")
        print(f"Snippet: {text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
