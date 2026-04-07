import os
from typing import Optional
from pypdf import PdfReader
from docx import Document

class ResumeManager:
    """Handles extraction of text from local resume files (PDF/Docx)."""
    
    @staticmethod
    def extract_text(file_path: str) -> Optional[str]:
        """Extract text from the given file path."""
        if not os.path.exists(file_path):
            print(f"[REDCLAW] Warning: Resume file not found at {file_path}")
            return None
            
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == ".pdf":
                reader = PdfReader(file_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
                
            elif ext == ".docx":
                doc = Document(file_path)
                text = "\n".join([para.text for para in doc.paragraphs])
                return text.strip()
                
            else:
                print(f"[REDCLAW] Warning: Unsupported file format {ext}")
                return None
        except Exception as e:
            print(f"[REDCLAW] Error extracting text from {file_path}: {e}")
            return None
