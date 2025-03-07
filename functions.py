from docx import Document
import pymupdf
import unicodedata
import ftfy


class DocumentConversionError(Exception):
    """Base exception for document conversion errors"""
    pass


def normalize_text(text):
    text = unicodedata.normalize('NFC', text)
    text = ftfy.fix_text(text) # Fix mojibake
    
    return text


def docx_to_txt(docx_stream):
    try:
        doc = Document(docx_stream)
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


def pdf_to_text(pdf_stream):
    try:
        doc = pymupdf.open(stream=pdf_stream)
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

