from flask import Flask, jsonify, request
from flask_httpauth import HTTPTokenAuth
from functions import docx_to_txt, pdf_to_markdown
import os


app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Planetary')


@auth.verify_token
def verify_token(token):
    if token == os.getenv('ACCESS_TOKEN'):
        return True
    return False

@app.post("/convert-to-text")
@auth.login_required
def convert():
    print(request.headers)

    # TODO: Better IP checking. Especially if behind a proxy this won't work.
    request_ip = request.remote_addr
    if request_ip != os.getenv('WHITELISTED_IP'):
        return jsonify({"error": "Invalid IP address"}), 401
    
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
