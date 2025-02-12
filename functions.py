from docx import Document
import pymupdf
import tempfile
from urllib.request import urlretrieve, urlopen
import os
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentConversionError(Exception):
    """Base exception for document conversion errors"""
    pass


def create_temp_file_from_url(file_url):
    start_time = time.time()
    logger.info(f"Starting download of file from: {file_url}")
    
    # Ensure temp directory exists
    custom_temp_dir = "temp-files"
    os.makedirs(custom_temp_dir, exist_ok=True)
    logger.info(f"Temp directory confirmed: {custom_temp_dir}")

    # Create a temporary file with a unique name
    with tempfile.NamedTemporaryFile(delete=False, dir=custom_temp_dir) as tmp_file:
        try:
            # First, check if the file is accessible
            logger.info("Checking file accessibility...")
            with urlopen(file_url) as response:
                content_length = response.headers.get('content-length')
                content_type = response.headers.get('content-type')
                logger.info(f"File accessible. Size: {content_length} bytes, Type: {content_type}")
            
            # Download file contents to temp file
            logger.info(f"Starting file download to: {tmp_file.name}")
            urlretrieve(file_url, tmp_file.name)
            
            download_time = time.time() - start_time
            logger.info(f"Download completed in {download_time:.2f} seconds")
            
            # Return the path to the temp new file
            return tmp_file.name
            
        except Exception as e:
            logger.error(f"Error during download: {str(e)}")
            # Clean up the temp file if it exists
            if os.path.exists(tmp_file.name):
                os.unlink(tmp_file.name)
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


def pdf_to_text(pdf_path):
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

