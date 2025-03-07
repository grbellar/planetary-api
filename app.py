from flask import Flask, jsonify, request, send_file
from flask_httpauth import HTTPTokenAuth
from functions import docx_to_txt, pdf_to_text
import os
from directus_functions import update_talent, get_all_talent_data, get_resume_file
from pprint import pprint


# TODO: Look into async support for multiple requests. FastAPI has async support. Maybe Flask does too.
app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')


@auth.verify_token
def verify_token(token):
    if token == os.getenv('ACCESS_TOKEN'):
        return True
    return False


@app.post("/convert-to-text")
@auth.login_required
def convert():
    data = request.json
    talent_id = data.get("talentId")
    print(f"Newly created Talent ID: {talent_id}")
        
    # Check if content-type is application/json. TODO: I don't think this is reachable. There is a built in check somewhere that 
    # fails before it gets here.
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    talent_data = get_all_talent_data(talent_id)
    # TODO: Add try catch for if file id not None. The resumeFile field could be empty
    resume_file_id = talent_data["data"]["resumeFile"]
    print(f"Resume File ID: {resume_file_id}")
    pprint(f"Talent Data: {talent_data}")
    file_stream, file_type = get_resume_file(resume_file_id)
    print(f"File Stream: {file_stream}")
    print(file_type)

    # if not file_url.endswith(('.docx', 'pdf')):
    #     return jsonify({"error": "Unsupported file format. File type must be a .docx, or .pdf"}), 400

    # if not file_url:
    #     return jsonify({"error": "fileUrl is required"}), 400
    
    # Convert Word
    if file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            text = docx_to_txt(file_stream)
            return update_talent(talent_id, text)
            # return jsonify({"good": "good"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # Convert PDF
    elif file_type == "application/pdf":
        try:
            text = pdf_to_text(file_stream)
            return update_talent(talent_id, text)
            # return jsonify({"text": text}), 200
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