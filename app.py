from flask import Flask, jsonify, request, send_file
from flask_httpauth import HTTPTokenAuth
from functions import docx_to_txt, pdf_to_markdown
import os
import ipaddress

# TODO: If I'm going to be sending files back to the client, I may need to look into asynchronous processing. FastAPI has async support.

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Planetary')
PROXY_HEADER_TYPES = [
        'True-Client-Ip',
        'X-Forwarded-For',
        'X-Real-Ip', 
        'CF-Connecting-Ip',
        'X-Client-Ip'
    ]
TRUSTED_PROXIES = os.getenv('TRUSTED_PROXIES').split(',')
WHITELISTED_IPS = [ipaddress.ip_address(ip) for ip in os.getenv('WHITELISTED_IPS').split(',')]

@auth.verify_token
def verify_token(token):
    if token == os.getenv('ACCESS_TOKEN'):
        return True
    return False


def allowed_ip(request):
    if request.remote_addr in TRUSTED_PROXIES:
        for proxy_type in PROXY_HEADER_TYPES:
            if proxy_type in request.headers:
                try:
                    client_ip = ipaddress.ip_address(request.headers[proxy_type])
                    return client_ip in WHITELISTED_IPS
                except Exception as e:
                    pass
    try:
        client_ip = ipaddress.ip_address(request.remote_addr)
        return client_ip in WHITELISTED_IPS
    except Exception as e:
        return False



@app.post("/convert-to-text")
@auth.login_required
def convert():

    if not allowed_ip(request):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Check if content-type is application/json
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    file_url = request.json.get('fileUrl')

    if not file_url.endswith(('.docx', 'pdf')):
        return jsonify({"error": "Unsupported file format. File type must be a .docx, or .pdf"}), 400

    if not file_url:
        return jsonify({"error": "fileUrl is required"}), 400
    
    # Convert Word
    if file_url.endswith('.docx'):
        try:
            text = docx_to_txt(file_url)
            return jsonify({"text": text}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # Convert PDF
    elif file_url.endswith('.pdf'):
        try:
            text = pdf_to_markdown(file_url)
            return jsonify({"text": text}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# TODO: Add logging, especially for exceptions that currently pass silently


@app.get("/get-file")
def get_file():
    file_path = 'spec.txt'
    try:
        return send_file(file_path, as_attachment=True, download_name='spec.txt')
    except FileNotFoundError:
        return "File not found", 404