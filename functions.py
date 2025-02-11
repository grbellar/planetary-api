from docx import Document
import pymupdf


class DocumentConversionError(Exception):
    """Base exception for document conversion errors"""
    pass

def docx_to_txt(docx_path):
    try:
        doc = Document(docx_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return text
    except FileNotFoundError:
        raise DocumentConversionError("DOCX file not found")
    except Exception as e:
        raise DocumentConversionError(f"Error processing DOCX file: {str(e)}")

def pdf_to_markdown(pdf_path):
    try:
        doc = pymupdf.open(pdf_path)
        text = []
        for page in doc:
            text.append(page.get_text())
        return text
    except FileNotFoundError:
        raise DocumentConversionError("PDF file not found")
    except Exception as e:
        raise DocumentConversionError(f"Error processing PDF file: {str(e)}")
