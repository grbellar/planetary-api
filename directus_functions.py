import requests
import os
from io import BytesIO

BASE_URL = os.getenv('BASE_DIRECTUS_URL')
HEADERS = {
    "Authorization": os.getenv('DIRECTUS_TOKEN')
}

def get_all_talent_data(talent_id):
    response = requests.get(f'{BASE_URL}/items/talent/{talent_id}', headers=HEADERS)
    return(response.json())


def update_talent(talent_id, resume_text):
    # Update talent resumeText record
    print("in update talent function")
    response = requests.patch(f'{BASE_URL}/items/talent/{talent_id}', headers=HEADERS, json={'resumeText': resume_text})
    print(response.json())
    return response.json()

def get_resume_file(file_id):
    file_content = requests.get(f"{BASE_URL}/assets/{file_id}", headers=HEADERS).content
    file_stream = BytesIO(file_content)
    return file_stream