from docx import Document
import pymupdf
import tempfile
from urllib.request import urlretrieve
import os
import unicodedata
import ftfy


class DocumentConversionError(Exception):
    """Base exception for document conversion errors"""
    pass


def create_temp_file_from_url(file_url):
    # Ensure temp directory exists
    custom_temp_dir = "temp-files"
    os.makedirs(custom_temp_dir, exist_ok=True)

    # Create a temporary file with a unique name
    with tempfile.NamedTemporaryFile(delete=False, dir=custom_temp_dir) as tmp_file:
        try:
            # Download file contents to temp file
            urlretrieve(file_url, tmp_file.name)
            # Return the path to the temp new file
            return tmp_file.name
        except Exception as e:
            raise Exception(f"Failed to download file: {str(e)}")


def normalize_text(text):
    text = unicodedata.normalize('NFC', text)
    text = ftfy.fix_text(text) # Fix mojibake
    
    return text


def docx_to_txt(docx_path):
    local_docx_path = create_temp_file_from_url(docx_path)
    try:
        doc = Document(local_docx_path)
        # Delete the temp file after the doc is created
        os.remove(local_docx_path)
        text_parts = []
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text:
                text = text.replace('\t', ' ')
                text_parts.append(text)
        return normalize_text(" ".join(text_parts))
    except FileNotFoundError:
        raise DocumentConversionError("DOCX file not found")
    except Exception as e:
        raise DocumentConversionError(f"Error processing DOCX file: {str(e)}")


def pdf_to_text(pdf_path):
    local_pdf_path = create_temp_file_from_url(pdf_path)
    try:
        doc = pymupdf.open(local_pdf_path)
        # Delete the temp file after the pdf is created
        os.remove(local_pdf_path)
        text = []
        for page in doc:
            # Strip newlines and whitespace from each page's text
            page_text = page.get_text().strip().replace('\n', ' ')
            text.append(page_text)
        return normalize_text(" ".join(text))
    except FileNotFoundError:
        raise DocumentConversionError("PDF file not found")
    except Exception as e:
        raise DocumentConversionError(f"Error processing PDF file: {str(e)}")

