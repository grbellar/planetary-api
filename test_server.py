import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_server_connection():
    url = 'https://planetary-api-llc9.onrender.com/static/grant.pdf'
    
    try:
        # Test HEAD request first
        head_response = requests.head(url, timeout=10)
        logger.info(f"HEAD request status: {head_response.status_code}")
        logger.info(f"Content-Type: {head_response.headers.get('content-type')}")
        logger.info(f"Content-Length: {head_response.headers.get('content-length')}")
        
        # Test GET request
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        # Check first few bytes
        first_bytes = next(response.iter_content(chunk_size=1024))
        logger.info(f"Successfully read first {len(first_bytes)} bytes")
        
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Connection test failed: {str(e)}")
        return False

# Run test
test_server_connection()