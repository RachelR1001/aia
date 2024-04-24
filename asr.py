import os
import requests
import pdb

AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
AZURE_WHISPER_DEPLOY_ID = os.environ["AZURE_WHISPER_DEPLOY_ID"]
AZURE_OPENAI_API_KEY = os.environ["AZURE_OPENAI_API_KEY"]

def transcribe(file):

    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_WHISPER_DEPLOY_ID}/audio/transcriptions?api-version=2024-02-01"
    print('url', url)

    # HTTP headers for authorization
    headers = {
        # 'Content-Type': 'multipart/form-data', # Setting this will throw exception
        'api-key': f'{AZURE_OPENAI_API_KEY}'
    }
    
    # 
    files = {
        'file': (file, open(file, 'rb'), 'audio/wav')
    }
    # call api
    try:
        response = requests.post(url, headers=headers, files=files)
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error raised by inference endpoint: {e}")

    if response.status_code != 200:
        raise ValueError(f"Failed with response: {response.text}")

    return response.json()
    
if __name__ == '__main__':
    input_file = 'test.wav'
    res = transcribe(input_file)
    print(res['text'])
