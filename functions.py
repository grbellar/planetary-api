from docx import Document
import pymupdf
import tempfile
from urllib.request import urlretrieve
import os
import time


class DocumentConversionError(Exception):
    """Base exception for document conversion errors"""
    pass


def create_temp_file_from_url(file_url):
    # Create a temporary file with a unique name
    with tempfile.NamedTemporaryFile(delete=False, dir='temp-files') as tmp_file:
        try:
            # Download file contents to temp file
            urlretrieve(file_url, tmp_file.name)
            # Return the path to the temp new file
            print(tmp_file.name)
            return tmp_file.name
        except Exception as e:
            raise Exception(f"Failed to download file: {str(e)}")


def docx_to_txt(docx_path):
    local_docx_path = create_temp_file_from_url(docx_path)
    try:
        doc = Document(local_docx_path)
        # Delete the temp file after the doc is created
        os.remove(local_docx_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return text
    except FileNotFoundError:
        raise DocumentConversionError("DOCX file not found")
    except Exception as e:
        raise DocumentConversionError(f"Error processing DOCX file: {str(e)}")


def pdf_to_markdown(pdf_path):
    # TODO: Should strip the newline characters from the text
    local_pdf_path = create_temp_file_from_url(pdf_path)
    try:
        doc = pymupdf.open(local_pdf_path)
        # Delete the temp file after the pdf is created
        os.remove(local_pdf_path)
        text = []
        for page in doc:
            text.append(page.get_text())
        return text
    except FileNotFoundError:
        raise DocumentConversionError("PDF file not found")
    except Exception as e:
        raise DocumentConversionError(f"Error processing PDF file: {str(e)}")

